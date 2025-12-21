// @ts-nocheck
import { user } from './stores'

const url = import.meta.env.API_URL || "http://127.0.0.1:5000/api";

const checkResponseStatus = async (status) => {
    if (status == 'unauthorized') {
        sessionStorage.removeItem("user");
        user.set(null)
    }
}

const get = async (endpoint = '') => {
    try {
        const token = sessionStorage.getItem("token");
        const response = await fetch(url + endpoint, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
        });
        let res = await response.json()
        checkResponseStatus(res.status)
        return res;
    } catch (error) {
        console.log(error);
    }
}

const post = async (endpoint = '', data = {}) => {
    try {
        const token = sessionStorage.getItem("token");
        const response = await fetch(url + endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify(data)
        });
        let res = await response.json()
        checkResponseStatus(res.status)
        return res;
    } catch (error) {
        console.log(error);
    }
}

const put = async (endpoint = '', data = {}) => {
    try {
        const token = sessionStorage.getItem("token");
        const response = await fetch(url + endpoint, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify(data)
        });
        let res = await response.json()
        checkResponseStatus(res.status)
        return res;
    } catch (error) {
        console.log(error);
    }
}

const _delete = async (endpoint = '') => {
    try {
        const token = sessionStorage.getItem("token");
        const response = await fetch(url + endpoint, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
        });
        let res = await response.json()
        checkResponseStatus(res.status)
        return res;
    } catch (error) {
        console.log(error);
    }
}

const auth = async (endpoint = '', data = {}) => {
    try {
        const response = await fetch(url + endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        let res = await response.json()
        checkResponseStatus(res.status)
        return res;
    } catch (error) {
        console.log(error);
    }
}


export default { get, post, put, _delete, auth };