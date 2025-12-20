// @ts-nocheck

const checkForm = (form) => {
    for (const key in form) {
        if (form[key].value == "" || form[key].value == null) {
            return false;
        }
    }
    return true;
};
const checkEmail = (email) => {
    let regExp = /^([\w\.\+]{1,})([^\W])(@)([\w]{1,})(\.[\w]{1,})+$/;
    return regExp.test(email);
};
const checkPassword = (password) => {
    let regExp =
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return regExp.test(password);
};
const checkPasswordConfirmation = (password, password_check) => {
    if (password === password_check) {
        return true;
    } else {
        return false;
    }
};

export default { checkForm, checkEmail, checkPassword, checkPasswordConfirmation };