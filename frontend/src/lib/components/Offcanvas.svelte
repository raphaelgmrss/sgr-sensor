<script>
	import { Button, ButtonSet, Slider } from "carbon-components-svelte";
	import Play from "carbon-icons-svelte/lib/Play.svelte";
	import Stop from "carbon-icons-svelte/lib/Stop.svelte";

	let { opened, setpoints, sensorState } = $props();
	let width = 20;
</script>

<aside class="offcanvas" style="--w:{width}vw" class:opened>
	<nav>
		Setpoints
		<!-- {#if !sensorState}
			<Button
				kind="tertiary"
				icon={Play}
				on:click={() => {
					sensorState = !sensorState;
				}}
			>
				Run
			</Button>
		{:else}
			<Button
				icon={Stop}
				kind="danger-tertiary"
				on:click={() => {
					sensorState = !sensorState;
				}}
			>
				Stop
			</Button>
		{/if} -->
		{#await setpoints then setpoints}
			{#each setpoints as setpoint}
				{#if setpoint.group == "input"}
					<Slider labelText={setpoint.name} value={0} />
				{/if}
			{/each}
		{/await}
	</nav>
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
		width: var(--w);
	}

	nav {
		display: flex;
		flex-direction: column;
		padding: 1.5rem;
		gap: 1rem;
	}

	/* nav a {
		color: #ccc;
		text-decoration: none;
	}

	nav a:hover {
		color: white;
	} */
</style>
