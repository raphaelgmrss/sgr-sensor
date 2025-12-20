<script>
    import * as echarts from "echarts";
    import { onMount, onDestroy } from "svelte";

    let { series = [] } = $props();

    let chartEl;
    let chart;
    let resizeObserver;

    onMount(() => {
        chart = echarts.init(chartEl);

        chart.setOption({
            animation: false,

            legend: {
                top: 30,
            },

            grid: {
                left: 80,
                right: 20,
                top: 60,
                bottom: 30,
                containLabel: true,
            },

            tooltip: {
                trigger: "axis",
            },

            xAxis: {
                type: "time",
                boundaryGap: false,
            },

            yAxis: {
                type: "value",
                scale: true,
            },

            series: [],
        });

        resizeObserver = new ResizeObserver(() => chart.resize());
        resizeObserver.observe(chartEl);

        $effect(() => {
            if (!chart) return;

            const safeSeries = series.map((s) => ({
                ...s,
                data: s.data.map((p) => [p[0], p[1]]),
            }));

            chart.setOption({ series: safeSeries });
        });

        onDestroy(() => {
            resizeObserver.disconnect();
            chart.dispose();
        });
    });
</script>

<div class="chart-container">
    <div bind:this={chartEl} class="chart"></div>
</div>

<style>
    .chart-container {
        width: 100%;
        height: 100%;
        min-height: 300px;
    }

    .chart {
        width: 100%;
        height: 100%;
    }
</style>
