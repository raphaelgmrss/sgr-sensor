<script>
    import logo from "../../assets/sgr_logo.svg";
</script>

<nav class="navbar">
    <div class="left">
        <img
            src={logo}
            style="width: auto; height: 56px; margin-left: 12px;"
            alt="stem-logo"
        />
        <!-- <span class="title">SGR Sensor</span> -->
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
        color: #fff;
    }

    .left {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .title {
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
