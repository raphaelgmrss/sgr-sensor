<script>
    import { onMount, onDestroy } from "svelte";
    import { user } from "../../utils/stores";

    import { OverflowMenu, OverflowMenuItem } from "carbon-components-svelte";
    import User from "carbon-icons-svelte/lib/User.svelte";

    import logo from "../../assets/sgr_logo.svg";

    let { profile = $bindable() } = $props();

    // Calbacks
    const clickProfile = () => {
        profile = true;
    };

    const signOut = () => {
        sessionStorage.clear();
        $user = null;
    };

    onMount(async () => {});
</script>

<nav class="navbar">
    <div class="left">
        <img
            src={logo}
            style="width: auto; height: 56px; margin-left: 12px;"
            alt="stem-logo"
        />
    </div>

    <div class="options">
        <span style="margin-right: 8px;">{$user.name}</span>
        <OverflowMenu flipped icon={User}>
            <OverflowMenuItem text={"Perfil"} on:click={clickProfile} />
            <OverflowMenuItem text={"Sair"} on:click={signOut} />
        </OverflowMenu>
    </div>
</nav>

<style>
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 56px;
        padding: 0 1rem;
        background: #e8e8e8;
    }

    .left {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .options {
        display: flex;
        height: 100%;
        flex: 1 1 0%;
        justify-content: flex-end;
        align-items: center;
        margin-right: 12px;
    }
</style>
