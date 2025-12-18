<script>
	// @ts-nocheck
	import { onMount, onDestroy } from "svelte";
	let { sensor, signals, opened, width } = $props();

	import { Button, Slider } from "carbon-components-svelte";

	import api from "../../utils/api";

	// Data
	let sensorState = $state();

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

	onMount(() => {});
	onDestroy(() => {});
</script>

<aside class="offcanvas" style="--w:{width}vw" class:opened>
	<nav>
		<div style="all:revert">
			{#if !sensorState}
				<Button
					size="field"
					kind="tertiary"
					on:click={() => {
						runSensor(sensor.id);
						sensorState = !sensorState;
					}}
				>
					Run
				</Button>
			{:else}
				<Button
					size="field"
					kind="danger-tertiary"
					on:click={() => {
						stopSensor(sensor.id);
						sensorState = !sensorState;
					}}
				>
					Stop
				</Button>
			{/if}
		</div>
		<br />
		{#each signals as signal}
			{#if signal.group == "input"}
				<Slider
					labelText={`${signal.name} [${signal.unit}]`}
					min={signal.setpoint_min}
					max={signal.setpoint_max}
					step={signal.setpoint_step}
					value={signal.setpoint}
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

		width: var(--w);
		height: 100%;

		transform: translateX(calc(-1 * var(--w)));
		transition: transform 0.25s ease;

		border-right: solid;
		border-color: #e8e8e8;
		border-width: thin;
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
</style>
