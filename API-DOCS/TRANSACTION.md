# Transaction API

## Table of Contents

#### [<= Back](./README.md)

#### NOTE: This document is not yet complete.

---

## /transaction/info

**HTTP Method**: POST
**Description**: Get Items in Transaction

### Request:

| Field | Type   | Required | Default | Description        |
|-------|--------|----------|---------|--------------------|
| token | String | Yes      | -       | Google OAuth Token |

### Response:

| status | statusText | data.msg |
|--------|------------|----------|

### Examples:

```js

```

## /transaction/create

**HTTP Method**: POST

**Description**: Add Transaction To Group

### Request:

| Field | Type   | Required | Default | Description        |
|-------|--------|----------|---------|--------------------|
| token | String | Yes      | -       | Google OAuth Token |

### Response:

| status | statusText | data.msg |
|--------|------------|----------|

### Examples:

```js

```

---

## /transaction/add

**HTTP Method**: POST

**Description**: Add Item to Transaction

### Request:

| Field | Type   | Required | Default | Description        |
|-------|--------|----------|---------|--------------------|
| token | String | Yes      | -       | Google OAuth Token |

### Response:

| status | statusText | data.msg |
|--------|------------|----------|

### Examples:

```js

```

---

## /transaction/update

**HTTP Method**: POST

**Description**: Change Item in Transaction

### Request:

| Field | Type   | Required | Default | Description        |
|-------|--------|----------|---------|--------------------|
| token | String | Yes      | -       | Google OAuth Token |

### Response:

| status | statusText | data.msg |
|--------|------------|----------|

### Examples:

```js

```


