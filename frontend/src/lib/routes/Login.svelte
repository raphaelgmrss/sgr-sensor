<script>
    // @ts-nocheck

    import { onMount, onDestroy } from "svelte";
    import { navigate } from "svelte-routing";

    import {
        Form,
        FormGroup,
        TextInput,
        PasswordInput,
        Button,
        Link,
        InlineNotification,
        Modal,
        Tile,
    } from "carbon-components-svelte";

    import { user, platformName } from "../../utils/stores";

    import api from "../../utils/api";
    import validator from "../../utils/validator";

    import logo from "../../assets/sgr_logo.svg";

    let term = {
        title: "Entre",
        email: "E-mail",
        password: "Senha",
        restore: "Recupere seu acesso",
        register: "Cadastre-se",
        login: "Entrar",
        successTitle: "Sucesso: ",
        errorTitle: "Erro: ",
        invalidCredentials: "Por favor, informe e-mail e senha válidos.",
        invalidEmailCredential: "Por favor, informe um e-mail cadastrado.",
        invalidForm: "Por favor, preencha todos os campos do formulário.",
        invalidEmail: "Por favor, informe um e-mail válido.",
        restoreSuccess:
            "Por favor, verifique a senha gerada em sua caixa de entrada.",
        emailMessage:
            "Por favor, informe seu e-mail para receber uma nova senha.",
    };
    let form = $state({
        login: {
            email: { value: null, invalid: false },
            password: { value: null, invalid: false },
        },
        restore: {
            email: { value: null, invalid: false },
        },
    });
    let alert = $state({
        login: {
            state: false,
            title: null,
            subtitle: null,
        },
        restore: {
            state: false,
            title: null,
            subtitle: null,
        },
    });
    let modal = $state(false);
    let timeout = 5000;

    const login = async () => {
        try {
            let invalidForm = !validator.checkForm(form.login);
            if (invalidForm) {
                alert.login.state = true;
                alert.login.title = term.errorTitle;
                alert.login.subtitle = term.invalidForm;
                return true;
            }

            const res = await api.auth("/auth/login", {
                email: form.login.email.value,
                password: form.login.password.value,
            });
            if (res.status == "success") {
                let { id, company_id, name, last_name, email, role } = res.data;
                $user = {
                    id: id,
                    name: name,
                    last_name: last_name,
                    email: email,
                    role: role,
                };

                sessionStorage.setItem("user", JSON.stringify($user));
                sessionStorage.setItem("token", res.token);

                navigate("/", { replace: true });
            } else if (res.status == "fail") {
                alert.login.state = true;
                alert.login.title = term.errorTitle;
                alert.login.subtitle = term.invalidCredentials;
            }
        } catch (error) {
            console.log(error);
        }
    };

    const restorePassword = async () => {
        try {
            let invalidForm = !validator.checkForm(form.restore);
            form.restore.email.invalid = !validator.checkEmail(
                form.restore.email.value,
            );
            if (invalidForm) {
                alert.restore.state = true;
                alert.restore.title = term.errorTitle;
                alert.restore.subtitle = term.invalidForm;
                return true;
            }

            if (form.restore.email.invalid) {
                alert.restore.subtitle = term.invalidForm;
                return true;
            }

            const res = await api.auth("/auth/password/restore", {
                email: form.restore.email.value,
            });
            if (res.status == "success") {
                alert.restore.state = true;
                alert.restore.kind = "success";
                alert.restore.title = term.successTitle;
                alert.restore.subtitle = term.restoreSuccess;
            } else if (res.status == "fail") {
                alert.restore.state = true;
                alert.restore.kind = "error";
                alert.restore.title = term.errorTitle;
                alert.restore.subtitle = term.invalidEmailCredential;
            }
        } catch (error) {
            console.log(error);
        }
    };

    $effect(() => {
        if ($user !== null) {
            navigate("/", { replace: true });
        }
    });

    onMount(() => {});
</script>

<div class="container">
    {#if alert.login.state}
        <div class="alert">
            <InlineNotification
                lowContrast
                title={""}
                subtitle={alert.login.subtitle}
                {timeout}
                on:close={() => {
                    alert.login.state = false;
                }}
            />
        </div>
    {/if}

    <Tile light>
        <!-- <div>
            <img class="logo" src={logo} alt="logo" />
        </div> -->

        <div style="margin-bottom: 2rem;">
            <h2 style="font-weight: bold; letter-spacing: 2px">
                {platformName}
            </h2>
        </div>

        <div class="form">
            <Form
                on:submit={(e) => {
                    e.preventDefault();
                    login();
                }}
            >
                <FormGroup>
                    <TextInput
                        light={true}
                        labelText={term.email}
                        placeholder=""
                        bind:value={form.login.email.value}
                    />
                </FormGroup>
                <FormGroup>
                    <PasswordInput
                        light={true}
                        labelText={term.password}
                        placeholder=""
                        bind:value={form.login.password.value}
                    />
                </FormGroup>
                <!-- <FormGroup>
                        <Link
                            href="/"
                            on:click={(e) => {
                                e.preventDefault();
                                modal = true;
                            }}
                        >
                            {term.restore}
                        </Link>
                    </FormGroup> -->
                <Button kind="primary" type="submit">
                    {term.login}
                </Button>
            </Form>
        </div>
    </Tile>
</div>

<!-- Password Restore Modal -->
<Modal
    size="sm"
    open={modal}
    modalHeading={""}
    primaryButtonText={"Solicitar"}
    secondaryButtonText={"Cancelar"}
    on:click:button--secondary={() => (modal = false)}
    on:click:button--primary={() => {
        alert.restore.state = false;
        restorePassword();
    }}
    on:open
    on:close={() => {
        modal = false;
    }}
>
    <p>{term.emailMessage}</p>
    <br />
    <Form
        on:submit={(e) => {
            e.preventDefault();
        }}
    >
        <FormGroup>
            <TextInput
                labelText={term.email}
                placeholder=""
                invalid={form.restore.email.invalid}
                invalidText={term.invalidEmail}
                bind:value={form.restore.email.value}
            />
        </FormGroup>
    </Form>
    {#if alert.restore.state}
        <InlineNotification
            lowContrast
            kind={alert.restore.kind}
            title={""}
            subtitle={alert.restore.subtitle}
            {timeout}
            on:close={() => {
                alert.restore.state = false;
            }}
        />
    {/if}
</Modal>

<style>
    .container {
        height: 100vh;
        width: 100vw;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        /* background-color: #f4f4f4; */
    }

    .logo {
        height: 128px;
        margin-bottom: 32px;
        animation: rotate 5s linear infinite;
        transform-origin: 50% 50%;
    }

    @keyframes rotate {
        from {
            transform: rotate(360deg);
        }
        to {
            transform: rotate(0deg);
        }
    }

    .alert {
        position: absolute;
        z-index: 1000;
        bottom: 12px;
    }

    /* .title {
        font-size: 20px;
        font-weight: 500;
    } */

    @media only screen and (min-width: 576px) {
        .form {
            width: 576px;
            margin-bottom: 48px;
        }
    }

    @media only screen and (max-width: 576px) {
        .form {
            width: 70vw;
            margin-bottom: 48px;
        }
    }
</style>
