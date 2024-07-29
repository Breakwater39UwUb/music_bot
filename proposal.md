# music bot proposal

- [music bot proposal](#music-bot-proposal)
  - [System requirements analysis](#system-requirements-analysis)
    - [Implementation suggestions](#implementation-suggestions)
      - [Database](#database)
  - [Use case analysis](#use-case-analysis)
  - [ER-Model](#er-model)

## System requirements analysis

The music bot should be able to find songs easily by
given conditions, such like song type, melody, language, lyrics,
instruments for song attributes and artist, composer, singer for creators.

Here are 2 types of how users share songs in the channels.

First, users could share songs, users share songs via a link,
whether it's on YouTube/YouTube Music, Spotify, Apple Music etc.
The system finds all attributes automatically.

Second, users have to clearly write down song name,

In anyway, users who shared songs should leave a comment why they share the song.

Once a song is shared, the system check if this song has already been shared and remind the duplicate sharing. Also the recommender will be recorded.
The bot would list top 10 songs that had been most searched or reacted each week.

### Implementation suggestions

#### Database

Relationship of song urls may filled by user,
otherwise, the bot should scrape the song urls from web.

Relationship of recommender, if we should not store discord user informations,
this database relationship should remove.

## Use case analysis

actors:

1. moderator
2. discord user

use case:

1. recommend songs
2. find songs

## ER-Model

Entities:

1. No
   1. Serial number to store records.
2. song_title
   1. Song title.
3. artist
   1. Artist(singer or band) of song.
4. song_tags
   1. Any tag of song.
5. recommender
   1. User who recommend the song.
6. comment
   1. Comment that recommender recommend the song.
7. links
   1. Links to the song.

Relationships:

1. linked_url
   1. The urls of the song on different platforms.
2. has_tags
   1. Relationships of tags names.
3. recommended_by
   1. Song that recommended by user.
