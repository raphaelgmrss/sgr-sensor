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

    // let { children } = $props();

    // Data
    let sensor = $state({});
    let signals = $state([]);

    let offcanvas = $state({
        opened: false,
        icon: Menu,
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

    onMount(() => {});
    onDestroy(() => {});
</script>

<Navbar />

<div class="content">
    <Offcanvas bind:sensor bind:signals bind:opened={offcanvas.opened} />

    <main class="panel">
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
    .content {
        display: flex;
        height: calc(100vh - 56px);
    }

    .panel {
        flex: 1;
        height: 100vh;
    }
</style>
