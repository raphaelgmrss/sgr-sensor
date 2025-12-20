import { mount } from 'svelte'
import "carbon-components-svelte/css/all.css";
import App from './App.svelte'

const app = mount(App, {
  target: document.getElementById('app'),
})

export default app
