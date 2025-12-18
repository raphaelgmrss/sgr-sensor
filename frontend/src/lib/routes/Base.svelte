<script>
    // @ts-nocheck

    import { onMount, onDestroy } from "svelte";

    import { Button } from "carbon-components-svelte";
    import User from "carbon-icons-svelte/lib/User.svelte";
    import Menu from "carbon-icons-svelte/lib/Menu.svelte";
    import Close from "carbon-icons-svelte/lib/Close.svelte";

    import Navbar from "../components/Navbar.svelte";
    import Offcanvas from "../components/Offcanvas.svelte";

    import { user, sensorId } from "../../utils/stores";
    import api from "../../utils/api";

    let open = $state(false);
    const WIDTH = 240;

    // Data
    let sensor = $state({});
    let signals = $state([]);

    let offcanvas = $state({
        opened: false,
        icon: Menu,
        width: 25,
    });

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
            // console.log(res.data);
            return res.data;
        } catch (error) {
            console.log(error);
        }
    };

    sensor = readSensor(sensorId);
    signals = readSignals(sensorId);

    onMount(() => {
        // sensor = readSensor(sensorId);
        // signals = readSignals(sensorId);
    });
    onDestroy(() => {});
</script>

<Navbar />

<div class="layout">
    <!-- <Offcanvas bind:open width={WIDTH} /> -->
    {#await sensor then sensor}
        {#await signals then signals}
            <Offcanvas
                {sensor}
                {signals}
                bind:opened={offcanvas.opened}
                width={offcanvas.width}
            />
        {/await}
    {/await}

    <main
        class="main"
        style="--w:{offcanvas.width}vw"
        class:shifted={offcanvas.opened}
    >
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
    </main>
</div>

<style>
    .layout {
        position: relative;
        height: calc(100vh - 56px);
    }

    .main {
        height: 100%;
        padding: 1.5rem;

        transform: translateX(0);
        transition: transform 0.25s ease;
    }

    .main.shifted {
        transform: translateX(var(--w));
    }
</style>
