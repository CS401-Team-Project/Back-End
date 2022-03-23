# Group API

## Table of Contents

#### [/group/profile](#groupprofile-1)

#### [/group/create](#groupcreate-1)

#### [/group/update](#groupupdatee-1)

#### [/group/delete](#groupdelete-1)

#### [/group/invite-member](#groupinvitemember-1)

#### [/group/join](#groupjoin-1)

#### [/group/remove-member](#groupremovemember-1)

#### [/group/refresh-id](#grouprefresh-id-1)

---

## /group/profile

**HTTP Method**: POST

**Description**: Retrieve a Group's Information

**TODO Back-End**: Change `/group/get` to `/group/profile`

### Request:

| Field | Type   | Required | Default | Description        |
|-------|--------|----------|---------|--------------------|
| token | String | Yes      | -       | Google OAuth Token |
| id    | String | Yes      | -       | Group ID           |

### Response:

| status | statusText            | data.msg                                       |
|--------|-----------------------|------------------------------------------------|
| 200    | OK                    | Successfully retrieved group info.             |
| 400    | Bad Request           | Missing Required Field(s) / Invalid Type(s).   |
| 404    | Not Found             | Token is unauthorized or group does not exist. |
| 500    | Internal Server Error | An unexpected error occurred.                  |

#### Note:

- If the user hasn't yet joined the group, the response **will not include** the `restricted` and `permissions` object.
- Only once the user has joined the group, the response **will include** the `restricted` and `permissions` object.

### If the user has joined the group:

- `id`: The group's unique identifier. [String]
- `name`: The group's name. [String]
- `description`: The group's description. [String]
- `admin`: The group's admin unique identifier [String]
- `members`: The group members' unique identifiers. [Array of Strings]
- `permissions`: The group's permission settings [JSON]
- `restricted`: The group's restricted items. [Array of Strings]
    - `balance`: The group's balance. [Float]
    - `transactions`: The transactions associated with the group [Array]
    - `date`: [JSON]
        - `created`: The group's creation date [String]
        - `updated`: The group's last update date  [String]

### If the user has not yet joined the group:

- `id`: The group's unique identifier. [String]
- `name`: The group's name. [String]
- `description`: The group's description. [String]
- `admin`: The group's admin unique identifier [String]
- `members`: The group members' unique identifiers. [Array of Strings]

### Examples:

```js
axios.post('/group/profile', {
    token: '<TOKEN>',
    id: '<GROUP_ID>'
}).then(function (response) {
    console.log(response.data);
}).catch(function (error) {
    console.log(error);
});
```

---

## /group/create

**HTTP Method**: POST

**Description**: Create a new Group

### Request:

| Field | Type   | Required | Default | Description        |
|-------|--------|----------|---------|--------------------|
| token | String | Yes      | -       | Google OAuth Token |
| data  | JSON   | Yes      | -       | Group Data         |

**Note**: The `data` object may contain the following fields:

- **name**: The group's name [**Required**] [String]
- **description**: The group's description [Optional] [String]
- **members**: The users to invite to the group [Optional] [Array]
    - The current user is added as an admin by default.
    - If no members are specified, the admin will be able to invite new users later on.
    - If members are specified, they will be invited to join the group.

### Response:

| status | statusText            | data.msg                                      |
|--------|-----------------------|-----------------------------------------------|
| 201    | Created               | Group successfully created.                   |
| 400    | Bad Request           | Missing Required Field(s) / Invalid Type(s).  |
| 401    | Unauthorized          | Token is unauthorized to perform the request. |
| 500    | Internal Server Error | An unexpected error occurred.                 |

### Examples:

#### Create a new group:

```js
axios.post('/group/create', {
    token: '<Google OAuth Token>',
    data: {
        name: 'My Group', // Required
        description: 'This is my group.', // Optional
        members: ['<User 1 Email>', '<User 2 Email>'], // Optional
    }
}).then(function (response) {
    console.log(response);
}).catch(function (error) {
    console.log(error);
});
```

---

## /group/update

**HTTP Method**: POST

**Description**: Update a Group's profile

**Note**: This endpoint is only available to either:

- The group's admin (which created the group initially)
- A group's member where the group's permissions allow them to update the group profile

### Request:

| Field | Type   | Required | Default | Description        |
|-------|--------|----------|---------|--------------------|
| token | String | Yes      | -       | Google OAuth Token |
| id    | String | Yes      | -       | Group ID           |
| data  | JSON   | Yes      | -       | Group Data         |

#### Note:

1. The data object **must** contain the _key-value_ pairs of fields to update.
2. The data object may **only** contain the following fields:
    1. `name`: The group's name [**Optional**] [String]
    2. `description`: The group's description [Optional] [String]
    3. `permissions`: The group's permissions [JSON]
3. The data object may **not** contain the following fields:
    - `id`: The group's unique identifier [String]
    - `admin`: The group's admin unique identifier [String]
    - `members`: The group members' unique identifiers. [Array of Strings]
    - `restricted`: The group's restricted items. [Array of Strings]
        - `balance`: The group's balance. [Float]
        - `transactions`: The transactions associated with the group [Array]
        - `date`: [JSON]
            - `created`: The group's creation date [String]
            - `updated`: The group's last update date  [String]

### Response:

| status | statusText            | data.msg                                       |
|--------|-----------------------|------------------------------------------------|
| 200    | OK                    | Group successfully updated.                    |
| 400    | Bad Request           | Missing Required Field(s) / Invalid Type(s).   |
| 404    | Not Found             | Token is unauthorized or group does not exist. |
| 500    | Internal Server Error | An unexpected error occurred.                  |

### Examples:

#### Update Group Name

```js
axios.post('/group/update', {
    token: '<Google OAuth Token>',
    id: '<Group ID>',
    data: {
        name: 'My Group', // Required
    }
}).then(function (response) {
    console.log(response);
}).catch(function (error) {
    console.log(error);
});
```

## /group/delete

**HTTP Method**: POST

**Description**: Delete a Group

**Note**: This endpoint is only available to the group's admin (which created the group initially).

### Request:

| Field | Type   | Required | Default | Description        |
|-------|--------|----------|---------|--------------------|
| token | String | Yes      | -       | Google OAuth Token |
| id    | String | Yes      | -       | Group ID           |

### Response:

| status | statusText            | data.msg                                       |
|--------|-----------------------|------------------------------------------------|
| 200    | OK                    | Group successfully deleted.                    |
| 400    | Bad Request           | Missing Required Field(s) / Invalid Type(s).   |
| 404    | Not Found             | Token is unauthorized or group does not exist. |
| 500    | Internal Server Error | An unexpected error occurred.                  |

### Examples:

```js
axios.post('/group/delete', {
    token: '<Google OAuth Token>',
    id: '<Group ID>'
}).then(function (response) {
    console.log(response);
}).catch(function (error) {
    console.log(error);
});
```

---

## /group/invite-member

**HTTP Method**: POST

**Description**: Invite a member to a Group

**Note**: This endpoint is only available to:

- the group's admin (which created the group initially).
- regular group members where the group's admin allowed permission to invite members.

### Request:

| Field | Type   | Required | Default | Description            |
|-------|--------|----------|---------|------------------------|
| token | String | Yes      | -       | Google OAuth Token     |
| id    | String | Yes      | -       | Group ID               |
| email | String | Yes      | -       | Member Email to Invite |

### Response:

| status | statusText            | data.msg                                       |
|--------|-----------------------|------------------------------------------------|
| 200    | OK                    | Member successfully invited.                   |
| 400    | Bad Request           | Missing Required Field(s) / Invalid Type(s).   |
| 404    | Not Found             | Token is unauthorized or group does not exist. |
| 409    | Conflict              | Member already exists in group.                |
| 500    | Internal Server Error | An unexpected error occurred.                  |

### Examples:

```js
axios.post('/group/invite_member', {
    token: '<Google OAuth Token>',
    id: '<Group ID>',
    email: '<Member Email>'
}).then(function (response) {
    console.log(response);
}).catch(function (error) {
    console.log(error);
});
```

---

## /group/join

**HTTP Method**: POST

**Description**: Allows a user to join a group they have been invited to based on the group's unique identifier.

**Note**: The user must have been invited to the group in order to join it.

### Request:

| Field | Type   | Required | Default | Description        |
|-------|--------|----------|---------|--------------------|
| token | String | Yes      | -       | Google OAuth Token |
| id    | String | Yes      | -       | Group ID           |

### Response:

| status | statusText            | data.msg                                     |
|--------|-----------------------|----------------------------------------------|
| 200    | OK                    | User joined group.                           |
| 400    | Bad Request           | Missing Required Field(s) / Invalid Type(s). |
| 401    | Unauthorized          | User is not invited or group does not exist. |
| 409    | Conflict              | User is already a member of the group.       |
| 500    | Internal Server Error | An unexpected error occurred.                |

### Examples:

```js
axios.post('/group/join', {
    token: '<Google OAuth Token>',
    id: '<Group ID>'
}).then(function (response) {
    console.log(response);
}).catch(function (error) {
    console.log(error);
});
```

## /group/remove-member

**HTTP Method**: POST

**Description**: Remove a member from a Group

**Restrictions**:

- Only the group's admin (which created the group initially) can remove members, unless the group's admin allowed
  permission to remove members.
- Non-Admin members may not remove other members from the group, unless the group's admin allowed permission to remove
  members.
- A member may always remove themselves from the group.

### Request:

| Field  | Type   | Required | Default | Description         |
|--------|--------|----------|---------|---------------------|
| token  | String | Yes      | -       | Google OAuth Token  |
| id     | String | Yes      | -       | Group ID            |
| userid | String | Yes      | -       | Member ID to Remove |

### Response:

| status | statusText            | data.msg                                       |
|--------|-----------------------|------------------------------------------------|
| 200    | OK                    | Member successfully removed.                   |
| 400    | Bad Request           | Missing Required Field(s) / Invalid Type(s).   |
| 404    | Not Found             | Token is unauthorized or group does not exist. |
| 409    | Conflict              | Member is not a member of the group.           |
| 500    | Internal Server Error | An unexpected error occurred.                  |

### Examples:

```js
axios.post('/group/remove_member', {
    token: '<Google OAuth Token>',
    id: '<Group ID>',
    userid: '<Member ID>'
}).then(function (response) {
    console.log(response);
}).catch(function (error) {
    console.log(error);
});
```

---

## /group/refresh-id

**HTTP Method**: POST

**Description**: Refresh a Group's unique identifier.

**Note**: This identifier is shared by a group admin to allow other users to join the group.

**Restrictions**:

- Only the group's admin can refresh the group's unique identifier.
- The group's unique identifier can only be refreshed once every 1 hour.
- When the unique identifier is refreshed, there should NOT be duplicate group identifiers in the Database.

### Request:

| Field | Type   | Required | Default | Description  |
|-------|--------|----------|---------|--------------|
| token | String | Yes      | -       | Google OAuth |
| id    | String | Yes      | -       | Group ID     |

### Response:

| status | statusText            | data.msg                                          |
|--------|-----------------------|---------------------------------------------------|
| 200    | OK                    | Group's unique identifier successfully refreshed. |
| 400    | Bad Request           | Missing Required Field(s) / Invalid Type(s).      |
| 401    | Unauthorized          | Token is unauthorized or group does not exist.    |
| 500    | Internal Server Error | An unexpected error occurred.                     |

### Examples:

```js
axios.post('/group/refresh-id', {
    token: '<Google OAuth Token>',
    id: '<Group ID>'
}).then(function (response) {
    console.log(response);
}).catch(function (error) {
    console.log(error);
});
```
