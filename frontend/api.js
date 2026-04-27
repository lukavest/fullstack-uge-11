async function api_call(trail, method, body) {
    const url = "http://localhost:8000"
    const req_url = url + trail;
    console.log(`${req_url} ${method} ${body}`)

    try {
        const response = await fetch(req_url, {
            method: method,
            body: body,
            headers: { "Content-Type": "application/json" }
        });
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
        const result = await response.json();
        return result
    } catch (error) {
        console.error(error.message);
    }
}

async function api_get(trail) {
    return api_call(trail, "GET", null)
}

async function api_post(trail, method, body) {
    if (body != null) { body = JSON.stringify(body) }
    return api_call(trail, method, body)
}

export { api_call, api_get, api_post };
