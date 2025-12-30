import { readable, writable } from "svelte/store";

export const user = writable(null);

export const platformName = readable("SGR Sensor");

export const sensorId = writable(undefined);
export const sensorState = writable(false);

export const samplingPeriod = writable(1000);
export const limit = writable(60);
export const norm = writable(false);