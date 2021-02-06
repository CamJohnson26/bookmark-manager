SELECT id, created_at, url, title, summary FROM url

DELETE FROM url
WHERE id IN(SELECT id FROM(SELECT  id,ROW_NUMBER() OVER(PARTITION BY url ORDER BY id)
AS row_num FROM url) t WHERE t.row_num > 1);

-----------------------------------------------
create table url
(
    id         serial not null
        constraint url_pk
            primary key,
    created_at timestamp default now(),
    url        varchar,
    title      varchar,
    text       varchar,
    html       varchar,
    summary    varchar
);

alter table url
    owner to doadmin;

create unique index url_id_uindex
    on url (id);

create unique index url_url_uindex
    on url (url);

