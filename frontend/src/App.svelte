<script>
  // @ts-nocheck

  import { onMount, onDestroy } from "svelte";

  import Base from "./lib/routes/Base.svelte";
  import Login from "./lib/routes/Login.svelte";

  import { user } from "./utils/stores";

  $user = JSON.parse(sessionStorage.getItem("user"));

  onMount(() => {});
  onDestroy(() => {});
</script>

<!-- {#if $user === null} -->
{#if false}
  <Login />
{:else}
  <Base />
{/if}
