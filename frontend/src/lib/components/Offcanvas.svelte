<script>
	// @ts-nocheck
	import { onMount, onDestroy } from "svelte";

	import {
		Button,
		Toggle,
		Slider,
		Select,
		SelectItem,
		Checkbox,
	} from "carbon-components-svelte";

	import { user, sensorId, sensorState, norm } from "../../utils/stores";
	import api from "../../utils/api";

	let { sensors, sensor, signals, opened, width, selectSensor } = $props();

	// Data

	const runSensor = async (id) => {
		try {
			const res = await api.get(`/sensor/${id}/start`);
			return res.data;
		} catch (error) {
			console.log(error);
		}
	};

	const stopSensor = async (id) => {
		try {
			const res = await api.get(`/sensor/${id}/stop`);
			return res.data;
		} catch (error) {
			console.log(error);
		}
	};

	const resetSensors = async () => {
		try {
			const res = await api.get(`/sensor/reset`);
			return res.data;
		} catch (error) {
			console.log(error);
		}
	};

	const setSignalValue = async (signalId, setpoint) => {
		try {
			let data = { setpoint: setpoint };
			let res = await api.put(`/signal/${signalId}`, data);
			return res.data;
		} catch (error) {
			console.log(error);
		}
	};

	const getSensorState = async (id) => {
		try {
			const res = await api.get(`/sensor/${id}/state`);
			return res.data;
		} catch (error) {
			console.log(error);
		}
	};

	onMount(async () => {
		if (typeof $sensorId === "number") {
			let res = await getSensorState($sensorId);
			$sensorState = res.state;
		}
	});

	onDestroy(() => {
		$sensorId = undefined;
		resetSensors();
	});
</script>

<aside class="offcanvas" style="--w:{width}vw" class:opened>
	<nav>
		<p>Sensor</p>
		<Select
			labelText="Sensores"
			noLabel={true}
			bind:selected={$sensorId}
			on:change={() => {
				$sensorState = false;
				$norm = false;
				resetSensors();
				selectSensor();
			}}
		>
			<SelectItem />
			{#each sensors as sensor}
				<SelectItem value={sensor.id} text={sensor.name} />
			{/each}
		</Select>

		{#if typeof $sensorId === "number"}
			<Toggle
				labelText=""
				hideLabel
				size="sm"
				labelA={"OFF"}
				labelB={"ON"}
				toggled={$sensorState}
				on:toggle={(e) => {
					if (!$sensorState) {
						runSensor($sensorId);
						$sensorState = true;
					} else {
						stopSensor($sensorId);
						$sensorState = false;
					}
				}}
			/>
			<br />
			<p>Setpoints</p>
			<Checkbox
				labelText="Normalize"
				bind:checked={$norm}
				disabled={!$sensorState}
			/>
			{#each signals as signal}
				{#if signal.group == "input"}
					<Slider
						labelText={`${signal.name} [${signal.unit}]`}
						min={signal.setpoint_min}
						max={signal.setpoint_max}
						step={signal.setpoint_step}
						value={signal.setpoint}
						minLabel={"❭"}
						maxLabel={" "}
						fullWidth={true}
						disabled={!$sensorState}
						on:change={(e) => {
							let setpoint = e.detail;
							setSignalValue(signal.id, setpoint);
						}}
					/>
				{/if}
			{/each}
		{/if}
	</nav>
</aside>

<style>
	.offcanvas {
		position: absolute;
		top: 0;
		left: 0;
		padding-top: 50px;

		width: var(--w);
		height: 100%;

		transform: translateX(calc(-1 * var(--w)));
		transition: transform 0.25s ease;

		border-right: solid;
		border-color: #e8e8e8;
		border-width: thin;

		overflow: auto;
	}

	.offcanvas.opened {
		transform: translateX(0);
	}

	nav {
		display: flex;
		flex-direction: column;
		padding: 1.5rem;
		gap: 1rem;
	}

	:root {
		--cds-support-02: #0f62fe;
	}

	:global(.bx--slider-text-input) {
		font-size: 0.75rem;
		flex: 0 0 auto;
	}
</style>
