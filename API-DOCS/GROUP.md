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


### Notes:

- If the user hasn't yet joined the group, the response **will not include** the `restricted` and `permissions` object.
- Only once the user has joined the group, the response **will include** the `restricted` and `permissions` object.

### Request:

| Field | Type   | Required | Default | Description        |
|-------|--------|----------|---------|--------------------|
| token | String | Yes      | -       | Google OAuth Token |
| id    | String | Yes      | -       | Group ID           |

### Response:

| status | statusText            | data.msg                                       |
|--------|-----------------------|------------------------------------------------|
| 200    | OK                    | Successfully retrieved the group profile.      |
| 400    | Bad Request           | Missing required field(s) or invalid type(s).  |
| 404    | Not Found             | Token is unauthorized or group does not exist. |
| 500    | Internal Server Error | An unexpected error occurred.                  |

#### Restrictions:

- The user must be an admin/member of the group OR must have been invited to the group.

#### If the user has joined the group:
- `msg`: description of response
- `data`: group data returned
  - `id`: The group's unique identifier. [String]
  - `name`: The group's name. [String]
  - `description`: The group's description. [String]
  - `admin`: The group's admin unique identifier [String]
  - `members`: The group members' unique identifiers. [Array of Strings]
  - `restricted`: The group's restricted items. [Array of Strings]
      - `permissions`: The group's permission settings [JSON]
      - `balance`: The group's balance. [Float]
      - `transactions`: The transactions associated with the group [Array]
      - `date`: [JSON]
          - `created`: The group's creation date [String]
          - `updated`: The group's last update date  [String]

#### If the user has not yet joined the group, but has been invited:
- `msg`: description of response
- `data`: group data returned
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

### Notes:

- Can be used by anyone.
- The current user is added as an admin by default.
- If no members are specified, the admin will be able to invite new users later on.
- If members are specified, they will be invited to join the group.

### Request:

| Field       | Type   | Required | Default            | Description                            |
|-------------|--------|----------|--------------------|----------------------------------------|
| token       | String | Yes      | -                  | Google OAuth Token                     |
| name        | String | Yes      | -                  | The group's name                       |
| description | String | No       | ""                 | The group's description                |
| members     | Array  | No       | [ <admin> ]        | The user emails to invite to the group |

#### Restrictions:

- Can only be called once every 5 minutes.

### Response:

| status | statusText            | data.msg                                       |
|--------|-----------------------|------------------------------------------------|
| 201    | Created               | Group successfully created.                    |
| 400    | Bad Request           | Missing required field(s) or invalid type(s).  |
| 404    | Not Found             | Token is unauthorized to perform this request. |
| 500    | Internal Server Error | An unexpected error occurred.                  |

### Examples:

#### Create a new group with a name, description, 2 initial members (+ admin):

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

#### Create a new group with a name, description, and no initial members:

```js
axios.post('/group/create', {
    token: '<Google OAuth Token>',
    name: 'My Group', // Required
    description: 'This is my group.', // Optional
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

### Notes:

- Can always be used by the group's admin (which created the group initially)

### Request:

| Field | Type   | Required | Default | Description                    |
|-------|--------|----------|---------|--------------------------------|
| token | String | Yes      | -       | Google OAuth Token             |
| id    | String | Yes      | -       | Group ID                       |
| data  | Object | Yes      | -       | Fields to update (JSON Object) |

#### Restrictions:

- Can only be used by a group's member if the group's permissions allow them to update the group profile
- **Should not** be able to update the `restricted` field.
- **Should not** be able to update the `admin` field, unless the user is the group's admin.
- **Should not** be able to update the `members` field
	- See [/group/invite-member](#groupinvite-member-1) and [/group/remove-member](#groupremove-member-1).

### Response:

| status | statusText            | data.msg                                       |
|--------|-----------------------|------------------------------------------------|
| 200    | OK                    | Successfully updated the group.                |
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

### Notes:

- Can only be used by the group's admin (which created the group initially)

### Request:

| Field | Type   | Required | Default | Description        |
|-------|--------|----------|---------|--------------------|
| token | String | Yes      | -       | Google OAuth Token |
| id    | String | Yes      | -       | Group ID           |

#### Restrictions:

- Cannot be used by group members, or anyone else but the admin.

### Response:

| status | statusText            | data.msg                                       |
|--------|-----------------------|------------------------------------------------|
| 200    | OK                    | Successfully deleted the group.                |
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

**Description**: Join a group

### Notes:

- A user may join a group based on the group's unique identifier (shared to them by the group's admin)

### Request:

| Field | Type   | Required | Default | Description        |
|-------|--------|----------|---------|--------------------|
| token | String | Yes      | -       | Google OAuth Token |
| id    | String | Yes      | -       | Group ID           |

#### Restrictions:

- Can only be used by a user who has not yet joined the group
- Can only be used by a user who has been invited to the group

### Response:

| status | statusText            | data.msg                                              |
|--------|-----------------------|-------------------------------------------------------|
| 200    | OK                    | Successfully joined the group.                        |
| 400    | Bad Request           | Missing required field(s) or invalid type(s).         |
| 404    | Not Found             | Token is unauthorized or the resource does not exist. |
| 409    | Conflict              | User is already a member of the group.                |
| 500    | Internal Server Error | An unexpected error occurred.                         |

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

### Notes:

- Can always be used by the group's admin (which created the group initially)

### Request:

| Field | Type   | Required | Default | Description            |
|-------|--------|----------|---------|------------------------|
| token | String | Yes      | -       | Google OAuth Token     |
| id    | String | Yes      | -       | Group ID               |
| email | String | Yes      | -       | Member Email to Invite |

#### Restrictions:

- Can be used by normal members if and only if the group's admin has allowed permission to invite members

### Response:

| status | statusText            | data.msg                                       |
|--------|-----------------------|------------------------------------------------|
| 200    | OK                    | Successfully invited the group member.         |
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

### Notes:

- Can always be used by the group's admin (which created the group initially)

- A member may always remove themselves from the group.

### Request:

| Field  | Type   | Required | Default | Description         |
|--------|--------|----------|---------|---------------------|
| token  | String | Yes      | -       | Google OAuth Token  |
| id     | String | Yes      | -       | Group ID            |
| userid | String | Yes      | -       | Member ID to Remove |

#### Restrictions:

- Can be used by normal members if and only if the group's admin has allowed permission to remove members

### Response:

| status | statusText            | data.msg                                       |
|--------|-----------------------|------------------------------------------------|
| 200    | OK                    | Successfully removed the group member.         |
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

### Notes:

- The group's unique identifier is used to allow other users to join the group.
- Only the group's admin can refresh the group's unique identifier

### Request:

| Field | Type   | Required | Default | Description  |
|-------|--------|----------|---------|--------------|
| token | String | Yes      | -       | Google OAuth |
| id    | String | Yes      | -       | Group ID     |

#### Restrictions:

- The group's unique identifier can only be refreshed once every 1 hour.

### Response:

| status | statusText            | data.msg                                       |
|--------|-----------------------|------------------------------------------------|
| 200    | OK                    | Successfully refreshed the group's unique ID.  |
| 400    | Bad Request           | Missing required field(s) or invalid type(s).  |
| 404    | Unauthorized          | Token is unauthorized or group does not exist. |
| 500    | Internal Server Error | An unexpected error occurred.                  |

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
