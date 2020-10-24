    Represents a message from Discord.

    There should be no need to create one of these manually.

    Attributes
    -----------
    tts: :class:`bool`
        Specifies if the message was done with text-to-speech.
        This can only be accurately received in :func:`on_message` due to
        a discord limitation.
    type: :class:`MessageType`
        The type of message. In most cases this should not be checked, but it is helpful
        in cases where it might be a system message for :attr:`system_content`.
    author: :class:`abc.User`
        A :class:`Member` that sent the message. If :attr:`channel` is a
        private channel or the user has the left the guild, then it is a :class:`User` instead.
    content: :class:`str`
        The actual contents of the message.
    nonce
        The value used by the discord guild and the client to verify that the message is successfully sent.
        This is typically non-important.
    embeds: List[:class:`Embed`]
        A list of embeds the message has.
    channel: Union[:class:`abc.Messageable`]
        The :class:`TextChannel` that the message was sent from.
        Could be a :class:`DMChannel` or :class:`GroupChannel` if it's a private message.
    call: Optional[:class:`CallMessage`]
        The call that the message refers to. This is only applicable to messages of type
        :attr:`MessageType.call`.
    reference: Optional[:class:`MessageReference`]
        The message that this message references. This is only applicable to
messages of
        type :attr:`MessageType.pins_add` or crossposted messages created by
a
        followed channel integration.

        .. versionadded:: 1.5

    mention_everyone: :class:`bool`
        Specifies if the message mentions everyone.

        .. note::

            This does not check if the ``@everyone`` or the ``@here`` text is in the message itself.
            Rather this boolean indicates if either the ``@everyone`` or the
``@here`` text is in the message
            **and** it did end up mentioning.
    mentions: List[:class:`abc.User`]
        A list of :class:`Member` that were mentioned. If the message is in a private message
        then the list will be of :class:`User` instead. For messages that are not of type
        :attr:`MessageType.default`\, this array can be used to aid in system messages.
        For more information, see :attr:`system_content`.

        .. warning::

            The order of the mentions list is not in any particular order so
you should
            not rely on it. This is a discord limitation, not one with the library.
    channel_mentions: List[:class:`abc.GuildChannel`]
        A list of :class:`abc.GuildChannel` that were mentioned. If the message is in a private message
        then the list is always empty.
    role_mentions: List[:class:`Role`]
        A list of :class:`Role` that were mentioned. If the message is in a private message
        then the list is always empty.
    id: :class:`int`
        The message ID.
    webhook_id: Optional[:class:`int`]
        If this message was sent by a webhook, then this is the webhook ID's
that sent this
        message.
    attachments: List[:class:`Attachment`]
        A list of attachments given to a message.
    pinned: :class:`bool`
        Specifies if the message is currently pinned.
    flags: :class:`MessageFlags`
        Extra features of the message.

        .. versionadded:: 1.3

    reactions : List[:class:`Reaction`]
        Reactions to a message. Reactions can be either custom emoji or standard unicode emoji.
    activity: Optional[:class:`dict`]
        The activity associated with this message. Sent with Rich-Presence related messages that for
        example, request joining, spectating, or listening to or with another member.

        It is a dictionary with the following optional keys:

        - ``type``: An integer denoting the type of message activity being requested.
        - ``party_id``: The party ID associated with the party.
    application: Optional[:class:`dict`]
        The rich presence enabled application associated with this message.

        It is a dictionary with the following keys:

        - ``id``: A string representing the application's ID.
        - ``name``: A string representing the application's name.
        - ``description``: A string representing the application's description.
        - ``icon``: A string representing the icon ID of the application.
        - ``cover_image``: A string representing the embed's image asset ID.