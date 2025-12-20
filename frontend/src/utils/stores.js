import { readable, writable } from "svelte/store";

export const user = writable(null);
export const route = writable({});

// App
export const platformName = "SGR Sensor";

// Sensor
export const sensorId = readable(1);;
export const sensorState = writable(false);

