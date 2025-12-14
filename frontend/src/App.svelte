<script>
  // @ts-nocheck

  import { Router, Route, Link, navigate } from "svelte-routing";

  import Base from "./lib/routes/Base.svelte";
  import Login from "./lib/routes/Login.svelte";

  import { user } from "./utils/stores";

  $user = JSON.parse(sessionStorage.getItem("user"));

  // if ($user === null) {
  //   navigate("/login", { replace: true });
  // }
</script>

<!-- {#if $user === null} -->
{#if false}
  <Router>
    <Route path="/"><Login /></Route>
    <Route path="/login"><Login /></Route>
  </Router>
{:else}
  <Router>
    <Route path="/"><Base /></Route>
  </Router>
{/if}
