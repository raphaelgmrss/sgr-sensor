<script>
	import { onMount, onDestroy } from "svelte";
	let { sensor, signals, opened } = $props();

	import { Button, Slider } from "carbon-components-svelte";

	import api from "../../utils/api";

	// Data
	let sensorState = $state();

	// Callbacks
	// const readSensor = async (id) => {
	// 	try {
	// 		const res = await api.get(`/sensor/${id}`);
	// 		// console.log(res.data);
	// 		return res.data;
	// 	} catch (error) {
	// 		console.log(error);
	// 	}
	// };
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

	onMount(() => {});
	onDestroy(() => {});
</script>

<aside class="offcanvas" class:opened>
	{#await sensor then sensor}
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
			<!-- Setpoints -->
			{#await signals then signals}
				{#each signals as signal}
					{#if signal.group == "input"}
						<Slider
							labelText={`${signal.name} [${signal.unit}]`}
							min={signal.setpoint_min}
							max={signal.setpoint_max}
							step={signal.setpoint_step}
							fullWidth
							value={signal.setpoint}
						/>
					{/if}
				{/each}
			{/await}
		</nav>
	{/await}
</aside>

<style>
	.offcanvas {
		width: 0;
		overflow: hidden;
		/* background: #1a1a1a; */
		/* color: white; */
		transition: width 0.3s ease;
		border-right: solid;
		border-color: #e8e8e8;
		border-width: thin;
	}

	.offcanvas.opened {
		width: 50vw;
	}

	nav {
		display: flex;
		flex-direction: column;
		padding: 1.5rem;
		gap: 1rem;
	}
</style>
