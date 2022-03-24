# Transaction API

## Table of Contents

#### [<= Back](./README.md)

#### [/transaction/info](#transactioninfo-1)

#### [/transaction/create](#transactioncreate-1)

#### [/transaction/update](#transactionupdate-1)

#### [/transaction/delete](#transactiondelete-1)

#### [/transaction/add-item](#transactionadd-item-1)

#### [/transaction/remove-item](#transactionremove-item-1)

#### [/item/info](#iteminfo-1)

#### NOTE: This document is not yet complete.

---

## /transaction/info

**HTTP Method**: POST
**Description**: Retrieve transaction information

### Request:

| Field | Type   | Required | Description        |
|-------|--------|----------|--------------------|
| token | String | Yes      | Google OAuth Token |
| id    | String | Yes      | Transaction ID     |

### Response:

| status | statusText            | data.msg                                             |
|--------|-----------------------|------------------------------------------------------|
| 200    | OK                    | Successfully retrieved transaction info.             |
| 400    | Bad Request           | Missing required field(s) or invalid type(s).        |
| 404    | Not Found             | Token is unauthorized or transaction does not exist. |
| 500    | Internal Server Error | An unexpected error occurred.                        |

### Notes:

- TODO

### Examples:

```js

```

## /transaction/create

**HTTP Method**: POST

**Description**: Create a new transaction

### Request:

| Field       | Type   | Required | Default           | Description             |
|-------------|--------|----------|-------------------|-------------------------|
| token       | String | Yes      | -                 | Google OAuth Token      |
| id          | String | Yes      | -                 | Group ID                |
| title       | String | Yes      | -                 | Transaction Title       |
| description | String | Yes      | -                 | Transaction Description |
| vendor      | String | Yes      | ""                | Transaction Vendor      |
| date        | String | No       | Current Date-Time | Transaction Date        |

### Response:

| status | statusText            | data.msg                                      |
|--------|-----------------------|-----------------------------------------------|
| 200    | OK                    | Successfully created transaction.             |
| 400    | Bad Request           | Missing required field(s) or invalid type(s). |
| 404    | Not Found             | Token is unauthorized.                        |
| 500    | Internal Server Error | An unexpected error occurred.                 |

### Notes:

- TODO

### Examples:

```js

```

---

## /transaction/update

**HTTP Method**: POST

**Description**: Update an existing transaction

### Request:

| Field | Type   | Required | Description                    |
|-------|--------|----------|--------------------------------|
| token | String | Yes      | Google OAuth Token             |
| id    | String | Yes      | Transaction ID                 |
| data  | Object | Yes      | Fields to update (JSON Object) |

### Response:

| status | statusText            | data.msg                                             |
|--------|-----------------------|------------------------------------------------------|
| 200    | OK                    | Successfully updated transaction.                    |
| 400    | Bad Request           | Missing required field(s) or invalid type(s).        |
| 404    | Not Found             | Token is unauthorized or transaction does not exist. |
| 500    | Internal Server Error | An unexpected error occurred.                        |

### Notes:

- TODO

### Examples:

```js

```

---

## /transaction/delete

**HTTP Method**: POST

**Description**: Delete an existing transaction

### Request:

| Field | Type   | Required | Description        |
|-------|--------|----------|--------------------|
| token | String | Yes      | Google OAuth Token |
| id    | String | Yes      | Transaction ID     |

### Response:

| status | statusText  | data.msg                                             |
|--------|-------------|------------------------------------------------------|
| 200    | OK          | Successfully deleted transaction.                    |
| 400    | Bad Request | Missing required field(s) or invalid type(s).        |
| 404    | Not Found   | Token is unauthorized or transaction does not exist. |
| 500    | Internal    | An unexpected error occurred.                        |

### Notes:

- TODO

### Examples:

```js

```

---

## /transaction/add-item

**HTTP Method**: POST

**Description**: Add an item to an existing transaction

### Request:

| Field       | Type   | Required | Description                     |
|-------------|--------|----------|---------------------------------|
| token       | String | Yes      | Google OAuth Token              |
| id          | String | Yes      | Transaction ID                  |
| name        | String | Yes      | Item ID                         |
| quantity    | Int    | Yes      | Quantity                        |
| unit_price  | Float  | Yes      | Unit Price                      |
| owed_by     | String | Yes      | User ID that owes for this item |
| description | String | No       | Description                     |

### Response:

| status | statusText | data.msg |
|--------|------------|----------|

### Notes:

- TODO

### Examples:

```js

```

---

## /transaction/remove-item

**HTTP Method**: POST

**Description**: Remove an item from an existing transaction

### Request:

| Field   | Type   | Required | Description        |
|---------|--------|----------|--------------------|
| token   | String | Yes      | Google OAuth Token |
| id      | String | Yes      | Transaction ID     |
| item_id | String | Yes      | Item ID            |

### Response:

| status | statusText  | data.msg                                                  |
|--------|-------------|-----------------------------------------------------------|
| 200    | OK          | Successfully removed item from transaction                |
| 400    | Bad Request | Missing required field(s) or invalid type(s).             |
| 404    | Not Found   | Token is unauthorized or transaction/item does not exist. |
| 500    | Internal    | An unexpected error occurred.                             |

### Notes:

- TODO

### Examples:

```js

```

---

## /item/info

**HTTP Method**: POST

**Description**: Retrieve information about an item

### Request:

| Field | Type   | Required | Description        |
|-------|--------|----------|--------------------|
| token | String | Yes      | Google OAuth Token |
| id    | String | Yes      | Item ID            |

### Response:

| status | statusText  | data.msg                                      |
|--------|-------------|-----------------------------------------------|
| 200    | OK          | Success                                       |
| 400    | Bad Request | Missing required field(s) or invalid type(s). |
| 404    | Not Found   | Item does not exist.                          |
| 500    | Internal    | An unexpected error occurred.                 |

### Notes:

- TODO

### Examples:

```js

```



