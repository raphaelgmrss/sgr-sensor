<script>
    import { onMount, onDestroy } from "svelte";
    import { user } from "../../utils/stores";
    import api from "../../utils/api";
    import validator from "../../utils/validator";
    import {
        Grid,
        Row,
        Column,
        Form,
        FormGroup,
        TextInput,
        PasswordInput,
        Button,
        InlineNotification,
        Modal,
    } from "carbon-components-svelte";

    // Properties
    let { opened = $bindable() } = $props();

    // Variables
    let dict = {
        profile: "Perfil",
        name: "Nome",
        last_name: "Sobrenome",
        email: "E-mail",
        password: "Senha",
        password_check: "Confirme a senha",
        save: "Salvar",
        cancel: "Cancelar",
        error_title: "Erro: ",
        invalid_credentials: "Por favor, informe credenciais válidas.",
        invalid_email: "Por favor, informe um e-mail válido",
        invalid_password:
            "Por favor, informe uma senha válida (pelo menos oito caracteres, uma letra minúscula, uma letra maiúscula, um número e um caractere especial).",
        invalid_password_check: "Por favor, informe a mesma senha.",
        invalid_form: "Por favor, preencha todos os campos do formulário.",
    };
    let form = $state({
        name: { value: null, invalid: false },
        last_name: { value: null, invalid: false },
        email: { value: null, invalid: false },
        password: { value: null, invalid: false },
        password_check: { value: null, invalid: false },
    });
    let invalid_form = false;
    let alert = {
        state: false,
        title: null,
        subtitle: null,
    };

    // Callbacks
    const updateProfile = async () => {
        try {
            invalid_form = !validator.checkForm(form);
            form.email.invalid = !validator.checkEmail(form.email.value);
            form.password.invalid = !validator.checkPassword(
                form.password.value,
            );
            form.password_check.invalid = !validator.checkPasswordConfirmation(
                form.password.value,
                form.password_check.value,
            );

            if (invalid_form) {
                alert.state = true;
                alert.title = dict.error_title;
                alert.subtitle = dict.invalid_form;
                return true;
            }
            if (
                form.email.invalid ||
                form.password.invalid ||
                form.password_check.invalid
            ) {
                return true;
            }

            const res = await api.put(`/user/${$user.id}`, {
                name: form.name.value,
                last_name: form.last_name.value,
                email: form.email.value,
                password: form.password.value,
            });
            if (res.status == "success") {
                let { id, company_id, email, name, lastName } = res.data;
                $user = {
                    id: id,
                    company_id: company_id,
                    email: email,
                    name: name,
                    lastName: lastName,
                };
                sessionStorage.setItem("user", JSON.stringify($user));
                opened = false;
            } else if (res.status == "fail") {
                alert.state = true;
                alert.title = dict.error_title;
                alert.subtitle = dict.invalid_credentials;
            }
        } catch (error) {
            console.log(error);
        }
    };

    onMount(async () => {
        const res = await api.get(`/user/${$user.id}`);
        if (res.status == "success") {
            form = {
                name: { value: null, invalid: false },
                last_name: { value: null, invalid: false },
                email: { value: null, invalid: false },
                password: { value: null, invalid: false },
                password_check: { value: null, invalid: false },
            };
            form.name.value = res.data.name;
            form.last_name.value = res.data.last_name;
            form.email.value = res.data.email;
        } else if (res.status == "fail") {
            alert.state = true;
            alert.title = dict.error_title;
            alert.subtitle = dict.invalid_credentials;
        }
    });
</script>

<Modal
    open={opened}
    modalHeading={dict.profile}
    primaryButtonText={dict.save}
    secondaryButtonText={dict.cancel}
    on:click:button--secondary={() => {
        opened = false;
    }}
    on:click:button--primary={() => {
        alert.state = false;
        updateProfile();
    }}
    on:open
    on:close={() => {
        opened = false;
    }}
>
    <Grid>
        <Row>
            <Column>
                {#if alert.state}
                    <InlineNotification
                        lowContrast
                        title={""}
                        subtitle={alert.subtitle}
                        on:close={() => {
                            alert.state = false;
                        }}
                    />
                {/if}
                <Form
                    on:submit={(e) => {
                        e.preventDefault();
                    }}
                >
                    <FormGroup>
                        <TextInput
                            labelText={dict.name}
                            placeholder=""
                            bind:value={form.name.value}
                        />
                    </FormGroup>
                    <FormGroup>
                        <TextInput
                            labelText={dict.last_name}
                            placeholder=""
                            bind:value={form.last_name.value}
                        />
                    </FormGroup>
                    <FormGroup>
                        <TextInput
                            labelText={dict.email}
                            placeholder=""
                            invalid={form.email.invalid}
                            invalidText={dict.invalid_email}
                            bind:value={form.email.value}
                        />
                    </FormGroup>
                    <FormGroup>
                        <PasswordInput
                            labelText={dict.password}
                            placeholder=""
                            invalid={form.password.invalid}
                            invalidText={dict.invalid_password}
                            bind:value={form.password.value}
                        />
                    </FormGroup>
                    <FormGroup>
                        <PasswordInput
                            labelText={dict.password_check}
                            placeholder=""
                            invalid={form.password_check.invalid}
                            invalidText={dict.invalid_password_check}
                            bind:value={form.password_check.value}
                        />
                    </FormGroup>
                </Form>
            </Column>
        </Row>
    </Grid>
</Modal>

<style>
</style>
