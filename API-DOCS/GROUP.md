# Group API

## Table of Contents

#### [<= Back](./README.md)

#### [/group/info](#groupinfo-1)

#### [/group/create](#groupcreate-1)

#### [/group/update](#groupupdate-1)

#### [/group/delete](#groupdelete-1)

#### [/group/join](#groupjoin-1)

#### [/group/invite-member](#groupinvite-member-1)

#### [/group/remove-member](#groupremove-member-1)

#### [/group/refresh-id](#grouprefresh-id-1)

---

## /group/info

**HTTP Method**: POST

**Description**: Retrieve a Group's Information

**TODO Back-End**: Change `/group/get` to `/group/info`

### Request:

| Field | Type   | Required | Default | Description        |
|-------|--------|----------|---------|--------------------|
| token | String | Yes      | -       | Google OAuth Token |
| id    | String | Yes      | -       | Group ID           |

### Response:

| status | statusText            | data.msg                                       |
|--------|-----------------------|------------------------------------------------|
| 200    | OK                    | Successfully retrieved group info.             |
| 400    | Bad Request           | Missing required field(s) or invalid type(s).  |
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
axios.post('/group/info', {
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

| Field       | Type   | Required | Default            | Description                            |
|-------------|--------|----------|--------------------|----------------------------------------|
| token       | String | Yes      | -                  | Google OAuth Token                     |
| name        | String | Yes      | -                  | The group's name                       |
| description | String | No       | ""                 | The group's description                |
| members     | Array  | No       | [ <admin> ]        | The user emails to invite to the group |
| permissions | Object | No       | DefaultPermissions | The group's permission settings        |

### Response:

| status | statusText            | data.msg                                      |
|--------|-----------------------|-----------------------------------------------|
| 201    | Created               | Group successfully created.                   |
| 400    | Bad Request           | Missing required field(s) or invalid type(s). |
| 401    | Unauthorized          | Token is unauthorized to perform the request. |
| 500    | Internal Server Error | An unexpected error occurred.                 |

### Notes:

- The current user is added as an admin by default.
- If no members are specified, the admin will be able to invite new users later on.
- If members are specified, they will be invited to join the group.

### Examples:

#### Create a new group:

```js
axios.post('/group/create', {
    token: '<Google OAuth Token>',
    name: 'My Group', // Required
    description: 'This is my group.', // Optional
    members: ['<User 1 Email>', '<User 2 Email>'], // Optional
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

| Field | Type   | Required | Default | Description                    |
|-------|--------|----------|---------|--------------------------------|
| token | String | Yes      | -       | Google OAuth Token             |
| id    | String | Yes      | -       | Group ID                       |
| data  | Object | Yes      | -       | Fields to update (JSON Object) |

#### Notes:

- **Should not** be able to update the `restricted` field.

### Response:

| status | statusText            | data.msg                                       |
|--------|-----------------------|------------------------------------------------|
| 200    | OK                    | Group successfully updated.                    |
| 400    | Bad Request           | Missing required field(s) or invalid type(s).  |
| 404    | Not Found             | Token is unauthorized or group does not exist. |
| 500    | Internal Server Error | An unexpected error occurred.                  |

### Examples:

#### Update Group Name

```js
axios.post('/group/update', {
    token: '<Google OAuth Token>',
    id: '<Group ID>', // Required
    data: {
        name: 'New Group Name'
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
| 400    | Bad Request           | Missing required field(s) or invalid type(s).  |
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

| status | statusText            | data.msg                                      |
|--------|-----------------------|-----------------------------------------------|
| 200    | OK                    | User joined group.                            |
| 400    | Bad Request           | Missing required field(s) or invalid type(s). |
| 401    | Unauthorized          | User is not invited or group does not exist.  |
| 409    | Conflict              | User is already a member of the group.        |
| 500    | Internal Server Error | An unexpected error occurred.                 |

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
| 400    | Bad Request           | Missing required field(s) or invalid type(s).  |
| 404    | Not Found             | Token is unauthorized or group does not exist. |
| 409    | Conflict              | Member already exists in group.                |
| 500    | Internal Server Error | An unexpected error occurred.                  |

### Examples:

```js
axios.post('/group/invite-member', {
    token: '<Google OAuth Token>',
    id: '<Group ID>',
    email: '<Member Email>'
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
| 400    | Bad Request           | Missing required field(s) or invalid type(s).  |
| 404    | Not Found             | Token is unauthorized or group does not exist. |
| 409    | Conflict              | Member is not a member of the group.           |
| 500    | Internal Server Error | An unexpected error occurred.                  |

### Examples:

```js
axios.post('/group/remove-member', {
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
| 400    | Bad Request           | Missing required field(s) or invalid type(s).     |
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
