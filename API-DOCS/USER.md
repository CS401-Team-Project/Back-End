# User API

## Table of Contents

#### [<= Back](./README.md)

#### [/register](#register-1)

#### [/user/info](#userinfo-1)

#### [/user/update](#userupdate-1)

#### [/user/delete](#userdelete-1)

---

## /register

**HTTP Method**: POST

**Description**: Create a new user account.

### Response:

| status | statusText            | data.msg                                      |
|--------|-----------------------|-----------------------------------------------|
| 201    | Created               | User successfully retrieved.                  |
| 200    | OK                    | User successfully retrieved.                  |
| 400    | Bad Request           | Missing required field(s) or invalid type(s). |
| 404    | Not Found             | Token is unauthorized or user does not exist. | 
| 500    | Internal Server Error | An unexpected error occurred.                 |

### Examples:

#### User logs in to their account:

```js
axios.post('/register', {}).then(function (response) {
    console.log(response);
}).catch(function (error) {
    console.log(error);
});
```

---

## /user/info

**HTTP Method**: POST

**Description**: Retrieves a user's profile.


### Request:

| Field | Type   | Required | Default | Description                  |
|-------|--------|----------|---------|------------------------------|
| sub   | String | No       | -       | Unique identifier for person |

### Response:

| status | statusText            | data.msg                                      |
|--------|-----------------------|-----------------------------------------------|
| 200    | OK                    | User successfully retrieved.      |
| 400    | Bad Request           | Missing required field(s) or invalid type(s). |
| 404    | Not Found             | Token is unauthorized or user does not exist. |
| 500    | Internal Server Error | An unexpected error occurred.                 |

#### Note:

- If sub is not provided:
	- Returns the current _user's private profile_ (all fields below)

- If sub is provided:
	- Returns a **user's public profile** for the given sub (**only** bolded fields).

### Private & Public Profiles:

- **msg**: info about request [String]
- **data**: person object [JSON]
  - **sub**: The user's unique identifier. [String]
  - **first_name**: The user's first name. [String]
  - **last_name**: The user's last name. [String]
  - **email**: The user's email address. [String]
  - **email_verified**: Whether the user's email address has been verified. [Boolean]
  - **picture**: The current user's profile picture URL.  [String]
  - _groups_: Group IDs that the user is a member of. [Array]
  - **date**: [JSON]
      - **created**: The date & time the user joined the application. [String]
      - _updated_: The date & time the user's profile was last updated. [String]
      - _last_login_: The date & time the user last logged in. [String]
  - **pay_with**: [JSON]
      - **venmo**: The user's venmo username. [String]
      - **cashapp**: The user's cashapp username. [String]
      - **paypal**: The user's paypal email address. [String]
      - **preferred**: The user's preferred payment method (venmo, cashapp, or paypal). [String]

### Examples:

#### User gets their own private profile:

```js
axios.post('/user/info', {}).then(function (response) {
    console.log(response);
}).catch(function (error) {
    console.log(error);
});
```

#### User gets another person's public profile

```js
axios.post('/user/info', {
    sub: '<Unique identifier for person>'
}).then(function (response) {
    console.log(response);
}).catch(function (error) {
    console.log(error);
});
```

---

## /user/update

**HTTP Method**: POST

**Description**: Modify User Account

**Note**: This endpoint is only available to the current user

### Request:

| Field | Type   | Required | Default | Description                    |
|-------|--------|----------|---------|--------------------------------|
| data  | Object | Yes      | -       | Fields to update (JSON Object) |

#### Note:

1. The data object **must** contain the _key-value_ pairs of fields to update.
2. The data object can **only** contain the following fields:
	- **first_name**: The user's first name [Optional] [String]
	- **last_name**: The user's last name [Optional] [String]
	- **picture**: The current user's profile picture URL Optional] [String]
	- **pay_with**: [Optional] [JSON]
		- **venmo**: The user's venmo username [Optional] [String]
		- **cashapp**: The user's cashapp username [Optional] [String]
		- **paypal**: The user's paypal email address [Optional] [String]
		- **preferred**: The user's preferred payment method (venmo, cashapp, or paypal) [Optional] [String]
3. The data object **should not** contain the following fields:
	- _sub_: The current user's [self] unique identifier [String]
	- **email**: The user's email address [String]
	- **email_verified**: Whether the user's email address has been verified [Boolean]
	- _groups_: Group IDs that the user is a member of [Array]
	- **date**: [JSON]
		- **created**: The date & time the user joined the application [String]
		- _updated_: The date & time the user's profile was last updated [String]
		- _last_login_: The date & time the user last logged in [String]

### Response:

| status | statusText            | data.msg                                      |
|--------|-----------------------|-----------------------------------------------|
| 200    | OK                    | Successfully updated the user profile.        |
| 400    | Bad Request           | Missing required field(s) or invalid type(s). |
| 404    | Not Found             | Token is unauthorized or user does not exist. |
| 500    | Internal Server Error | An unexpected error occurred.                 |

### Examples:

#### User changes their first name only:

```js
axios.post('/user/update', {
    data: {
        first_name: 'John',
    }
}).then(function (response) {
    console.log(response);
}).catch(function (error) {
    console.log(error);
});
```

#### User changes their first and last name:

```js
axios.post('/user/update', {
    data: {
        first_name: 'John',
        last_name: 'Doe',
    }
}).then(function (response) {
    console.log(response);
}).catch(function (error) {
    console.log(error);
});
```

#### User changes 2 of their payment profiles:

```js
axios.post('/user/update', {
    data: {
        pay_with: {
            venmo: 'johndoe',
            cashapp: 'johndoe',
        }
    }
}).then(function (response) {
    console.log(response);
}).catch(function (error) {
    console.log(error);
});
```

---

## /user/delete

**HTTP Method**: POST

**Description**: Delete User Account

**Note**: This endpoint is only available to the current user

### Response:

| status | statusText            | data.msg                                      |
|--------|-----------------------|-----------------------------------------------|
| 200    | OK                    | Successfully deleted the user profile.        |
| 404    | Not Found             | Token is unauthorized or user does not exist. |
| 500    | Internal Server Error | An unexpected error occurred.                 |

### Examples:

#### User deletes their account:

```js
axios.post('/user/delete', {}).then(function (response) {
    console.log(response);
}).catch(function (error) {
    console.log(error);
});
```