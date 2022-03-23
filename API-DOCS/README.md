# API Definition:

## Table of Contents:

### [/user](./USER.md)

### [/group](./GROUP.md)

### [/transaction](./TRANSACTION.md)

---

# HTTP Spec:

Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#server_error_responses

## Successful responses

### 200 OK

The request succeeded. The result meaning of "success" depends on the HTTP method:

- **GET**: The resource has been fetched and transmitted in the message body.
- **PUT** or **POST**: The resource describing the result of the action is transmitted in the message body.

### 201 Created

The request **succeeded**, and a **new resource was created** as a result.  
This is typically the response sent after POST requests, or some PUT requests.

## Client Error Responses:

### 400 Bad Request

The server cannot or will not process the request due to something that is perceived to be a client error

- E.g.: malformed request syntax, invalid request message framing, or deceptive request routing.

### 401 Unauthorized

Although the HTTP standard specifies "unauthorized", semantically this response means "unauthenticated".

- That is, the client must authenticate itself to get the requested response.

### 403 Forbidden

The client does not have access rights to the content;

- that is, it is unauthorized, so the server is refusing to give the requested resource.

Unlike 401 Unauthorized, the client's identity is known to the server.

### 404 Not Found

The server can not find the requested resource.

- In the browser, this means the URL is not recognized.
- In an API, this can also mean that the endpoint is valid but the resource itself does not exist.

Servers may also send this response instead of 403 Forbidden to hide the existence of a resource from an unauthorized
client.

## Server Error Responses

### 500 Internal Server Error

The server has encountered a situation it does not know how to handle.