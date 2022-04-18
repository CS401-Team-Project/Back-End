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
| id    | String | Yes      | Transaction ID     |

### Response:

| status | statusText            | data.msg                                             |
|--------|-----------------------|------------------------------------------------------|
| 200    | OK                    | Successfully retrieved the transaction's info.       |
| 400    | Bad Request           | Missing required field(s) or invalid type(s).        |
| 404    | Not Found             | Token is unauthorized or transaction does not exist. |
| 500    | Internal Server Error | An unexpected error occurred.                        |

### Notes:

- If the user is part of the group that the transaction belongs to,
returns transaction info and status code 200.
- If the user is not part of the group that the transaction belongs to,
returns 404 status code.

### Examples:

```js
axios.post('/transaction/info', {
    id: '<TRANSACTION_ID>'
}).then(response => {
    console.log(response.data);
}).catch(error => {
    console.log(error.response.data);
});
```

## /transaction/create

**HTTP Method**: POST

**Description**: Create a new transaction

### Request:

| Field    | Type   | Required | Default           | Description                                                         |
|----------|--------|----------|-------------------|---------------------------------------------------------------------|
| id       | String | Yes      | -                 | Group ID                                                            |
| title    | String | Yes      | -                 | Transaction Title                                                   |
| desc     | String | Yes      | -                 | Transaction Description                                             |
| vendor   | String | Yes      | ""                | Transaction Vendor                                                  |
| date     | String | No       | Current Date-Time | Transaction Date                                                    |
| who_paid | JSON   | Yes      | -                 | Dictionary of who paid and how much                                 |
| items    | List   | Yes      | -                 | List of jsons, Each json should contain fields required for an item |

### `items` Fields:

| Field      | Type   | Required | Default            | Description                         |
|------------|--------|----------|--------------------|-------------------------------------|
| name       | String | Yes      | -                  | Name of the Item                    |
| quantity   | Int    | Yes      | -                  | Number of Items                     |
| desc       | String | Yes      | -                  | The item's description              |
| unit_price | Float  | Yes      | -                  | Price of a single item              |
| owed_by    | String | Yes      | -                  | user sub of who the item belongs to |


### Response:

| status | statusText            | data.msg                                      |
|--------|-----------------------|-----------------------------------------------|
| 200    | OK                    | Successfully created the transaction.         |
| 400    | Bad Request           | Missing required field(s) or invalid type(s). |
| 404    | Not Found             | Token is unauthorized.                        |
| 500    | Internal Server Error | An unexpected error occurred.                 |

### Notes:

- If successful, returns status code 200 and a JSON Object of the transaction ID and
a message indicating that the transaction was created.

### Examples:

```js
axios.post('/transaction/create', {
    id: '<GROUP_ID>',
    title: '<TRANSACTION_TITLE>',
    description: '<TRANSACTION_DESCRIPTION>',
    vendor: '<TRANSACTION_VENDOR>',
    date: '<TRANSACTION_DATE>'
}).then(response => {
    console.log(response.data);
}).catch(error => {
    console.log(error.response.data);
});
```

---

## /transaction/update

**HTTP Method**: POST

**Description**: Update an existing transaction

### Request:

| Field | Type   | Required | Description                    |
|-------|--------|----------|--------------------------------|
| id    | String | Yes      | Transaction ID                 |
| data  | Object | Yes      | Fields to update (JSON Object) |

### Response:

| status | statusText            | data.msg                                             |
|--------|-----------------------|------------------------------------------------------|
| 200    | OK                    | Successfully updated the transaction.                |
| 400    | Bad Request           | Missing required field(s) or invalid type(s).        |
| 404    | Not Found             | Token is unauthorized or transaction does not exist. |
| 500    | Internal Server Error | An unexpected error occurred.                        |

### Notes:

- If successful, returns status code 200 and a JSON Object of the transaction ID and
a message indicating that the transaction was updated.

### Examples:

```js
axios.post('/transaction/update', {
    id: '<TRANSACTION_ID>',
    data: {
        title: '<TRANSACTION_TITLE>',
        description: '<TRANSACTION_DESCRIPTION>',
        vendor: '<TRANSACTION_VENDOR>',
        date: '<TRANSACTION_DATE>'
    }
}).then(response => {
    console.log(response.data);
}).catch(error => {
    console.log(error.response.data);
});
```

---

## /transaction/delete

**HTTP Method**: POST

**Description**: Delete an existing transaction

### Request:

| Field | Type   | Required | Description        |
|-------|--------|----------|--------------------|
| id    | String | Yes      | Transaction ID     |

### Response:

| status | statusText  | data.msg                                             |
|--------|-------------|------------------------------------------------------|
| 200    | OK          | Successfully deleted the transaction.                |
| 400    | Bad Request | Missing required field(s) or invalid type(s).        |
| 404    | Not Found   | Token is unauthorized or transaction does not exist. |
| 500    | Internal    | An unexpected error occurred.                        |

### Notes:

- If successful, returns status code 200 and a message indicating that the transaction was deleted.

### Examples:

```js
axios.post('/transaction/delete', {
    token: '<TOKEN>',
    id: '<TRANSACTION_ID>'
}).then(response => {
    console.log(response.data);
}).catch(error => {
    console.log(error.response.data);
});
```

---



## /item/info

**HTTP Method**: POST

**Description**: Retrieve information about an item

### Request:

| Field | Type   | Required | Description        |
|-------|--------|----------|--------------------|
| id    | String | Yes      | Item ID            |

### Response:

| status | statusText  | data.msg                                      |
|--------|-------------|-----------------------------------------------|
| 200    | OK          | Successfully retrieved the item info.         |
| 400    | Bad Request | Missing required field(s) or invalid type(s). |
| 404    | Not Found   | Item does not exist.                          |
| 500    | Internal    | An unexpected error occurred.                 |

### Notes:

- If successful, returns status code 200 and a JSON Object of the item.

### Examples:

```js
axios.post('/item/info', {
    id: '<ITEM_ID>'
}).then(response => {
    console.log(response.data);
}).catch(error => {
    console.log(error.response.data);
});
```



