<script>
    // @ts-nocheck

    import { onMount, onDestroy } from "svelte";
    import { navigate } from "svelte-routing";

    import { Button, ButtonSet, Slider } from "carbon-components-svelte";
    import User from "carbon-icons-svelte/lib/User.svelte";
    import Play from "carbon-icons-svelte/lib/Play.svelte";
    import Stop from "carbon-icons-svelte/lib/Stop.svelte";
    import ChartMultiLine from "carbon-icons-svelte/lib/ChartMultiLine.svelte";
    import Menu from "carbon-icons-svelte/lib/Menu.svelte";
    import Close from "carbon-icons-svelte/lib/Close.svelte";

    import Navbar from "../components/Navbar.svelte";
    import Offcanvas from "../components/Offcanvas.svelte";

    import {
        user,
        route,
        platformName,
        sensorId,
        // setpoints,
    } from "../../utils/stores";
    import api from "../../utils/api";

    let { children } = $props();

    // Data
    let sensor = $state({});
    let signals = $state([]);

    let offcanvas = $state({
        opened: false,
        icon: Menu,
    });

    let sensorState = $state(false);

    // Callbacks
    const readSensor = async (id) => {
        try {
            const res = await api.get(`/sensor/${id}`);
            // console.log(res.data);
            return res.data;
        } catch (error) {
            console.log(error);
        }
    };

    const readSignals = async (id) => {
        try {
            const res = await api.get(`/sensor/${id}/signals`);
            console.log(res.data);
            return res.data;
        } catch (error) {
            console.log(error);
        }
    };

    sensor = readSensor(sensorId);
    signals = readSignals(sensorId);

    // $effect(() => {
    //     $setpoints = signals;
    // });

    onMount(() => {});
    onDestroy(() => {});
</script>

<Navbar />

<div class="content">
    {#await sensor then sensor}
        <Offcanvas bind:opened={offcanvas.opened} bind:setpoints={signals} />
        <!-- {#await signals then signals}
        {/await} -->

        <main class="panel">
            <!-- <Button
                kind="tertiary"
                iconDescription="Setpoints"
                icon={offcanvas.icon}
                onclick={() => {
                    offcanvas.opened = !offcanvas.opened;
                    if (offcanvas.opened) {
                        offcanvas.icon = Close;
                    } else {
                        offcanvas.icon = Menu;
                    }
                }}
            >
                Setpoints
            </Button> -->
            <Button
                kind="ghost"
                iconDescription="Setpoints"
                hideTooltip={true}
                icon={offcanvas.icon}
                onclick={() => {
                    offcanvas.opened = !offcanvas.opened;
                    if (offcanvas.opened) {
                        offcanvas.icon = Close;
                    } else {
                        offcanvas.icon = Menu;
                    }
                }}
            />
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

            <!-- <Button
                icon={ChartMultiLine}
                kind="secondary"
                onclick={() => {
                    offcanvas.opened = !offcanvas.opened;
                }}>Setpoints</Button
            > -->

            <!-- {#await signals then signals}
                {#each signals as signal}
                    {#if signal.group == "input"}
                        <Slider labelText={signal.name} fullWidth value={0} />
                    {/if}
                {/each}
            {/await} -->
        </main>
    {/await}
</div>

<style>
    .content {
        display: flex;
        height: calc(100vh - 56px);
    }

    .panel {
        flex: 1;
        padding: 1.5rem;
        height: 100vh;
    }

    /* button {
        margin-bottom: 1rem;
    } */
</style>
