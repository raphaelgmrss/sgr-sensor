<script>
	// @ts-nocheck
	import { onMount, onDestroy } from "svelte";
	let { sensor, signals, opened, width } = $props();

	import { Button, Toggle, Slider } from "carbon-components-svelte";

	import { user, sensorId, sensorState } from "../../utils/stores";
	import api from "../../utils/api";

	// Data
	// let sensorState = $state();

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
		let res = await getSensorState($sensorId);
		$sensorState = res.state;
	});

	onDestroy(() => {
		stopSensor(sensorId);
	});
</script>

<aside class="offcanvas" style="--w:{width}vw" class:opened>
	<nav>
		<div>
			{sensor.name}
		</div>
		<br />
		<Toggle
			labelText="Sensor control"
			hideLabel
			size="sm"
			labelA={"OFF"}
			labelB={"ON"}
			toggled={$sensorState}
			on:toggle={(e) => {
				if (!$sensorState) {
					runSensor(sensor.id);
					$sensorState = true;
				} else {
					stopSensor(sensor.id);
					$sensorState = false;
				}
			}}
		/>
		<br />
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
					on:change={(e) => {
						let setpoint = e.detail;
						setSignalValue(signal.id, setpoint);
					}}
				/>
			{/if}
		{/each}
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
