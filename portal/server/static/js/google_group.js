

const groups = CloudIdentityGroups.Groups;



function createMembership(namespace, groupId, memberKey) {
  try {
    // Given a group ID and namespace, retrieve the ID for parent group
    const groupLookupResponse = groups.lookup({
      'groupKey.id': groupId,
      'groupKey.namespace': namespace
    });
    const groupName = groupLookupResponse.name;

    // Create a membership object with a memberKey and a single role of type MEMBER
    const membership = {
      preferredMemberKey: { id: memberKey },
      roles: [
        {
          name: "MEMBER",
          expiryDetail: {
            expireTime: "2025-10-02T15:01:23Z",
          },
        },
      ],
    };

    // Create a membership using the ID for the parent group and a membership object
    const response = groups.Memberships.create(membership, groupName);
    console.log(JSON.stringify(response));
  } catch (e) {
    console.error(e);
  }
}