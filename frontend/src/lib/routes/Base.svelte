<script>
    // @ts-nocheck

    import { onMount, onDestroy } from "svelte";

    import { Button } from "carbon-components-svelte";
    import User from "carbon-icons-svelte/lib/User.svelte";
    import Menu from "carbon-icons-svelte/lib/Menu.svelte";
    import Close from "carbon-icons-svelte/lib/Close.svelte";

    import Navbar from "../components/Navbar.svelte";
    import Offcanvas from "../components/Offcanvas.svelte";
    import Chart from "../components/Chart.svelte";

    import { user, sensorId, sensorState } from "../../utils/stores";
    import api from "../../utils/api";
    import { derived } from "svelte/store";

    let open = $state(false);

    // Data
    let sensor = $state({});
    let signals = $state([]);
    let points = $state([]);
    let samplingPeriod = 1000;
    let limit = 60;

    let pointsObj = {};
    let series = $state([]);
    let seriesObj = [];
    let intervalId = null;

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

    const getPoints = async (id) => {
        try {
            const res = await api.get(`/sensor/${id}/points?limit=${limit}`);
            // console.log(res.data);
            return res.data;
        } catch (error) {
            console.log(error);
        }
    };

    function startInterval() {
        if (intervalId === null) {
            intervalId = setInterval(async () => {
                points = await getPoints($sensorId);

                seriesObj = [];
                if (typeof points !== "undefined") {
                    for (const point of points) {
                        seriesObj.push({
                            name: point.name,
                            type: "line",
                            showSymbol: false,
                            smooth: true,
                            data: point.records,
                        });
                    }
                }
                series = seriesObj;
            }, samplingPeriod);
        }
    }

    function stopInterval() {
        if (intervalId !== null) {
            clearInterval(intervalId);
            intervalId = null;
        }
    }

    $effect(() => {
        if (!$sensorState) {
            stopInterval();
        } else {
            startInterval();
        }
    });

    onMount(async () => {
        sensor = await readSensor($sensorId);
        signals = await readSignals($sensorId);
        points = await getPoints($sensorId);

        samplingPeriod = sensor.sampling_period * 1e3;

        if (points && Array.isArray(points)) {
            pointsObj = {};
            for (const point of points) {
                pointsObj[point.name] = [];
            }
        }

        startInterval();
    });

    onDestroy(() => {
        clearInterval(intervalId);
    });
</script>

<Navbar />

<div class="layout">
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

    <div class="overlay-btn">
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
    </div>

    <main
        class="main"
        style="--w:{offcanvas.width}vw"
        class:shifted={offcanvas.opened}
    >
        <Chart {series} />
    </main>
</div>

<style>
    .layout {
        position: relative;
        height: calc(100vh - 56px);
    }

    .main {
        position: absolute;
        top: 0;
        right: 0;
        height: 100%;
        width: 100%;
        transition: width 0.25s ease;
    }

    .main.shifted {
        width: calc(100% - var(--w));
    }

    .overlay-btn {
        position: absolute;
        top: 12px;
        left: 12px;
        z-index: 10;
    }
</style>
