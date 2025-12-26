import { readable, writable } from "svelte/store";

export const user = writable(null);

export const platformName = readable("SGR Sensor");

export const sensorId = readable(1);;
export const sensorState = writable(false);

