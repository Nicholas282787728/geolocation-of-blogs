/*
This script creates 3 new tables in addition to 6 original tables.

Original tables:
+-------------------------+--------------------+
| Tables_in_myblogs       | Number of rows 	  |
+-------------------------+--------------------+
| blogs                   | 12,562			  |
| blogs_posts             | 2,303,343		  |
| posts                   | 2,303,755		  |
| profiles                | 6,750			  |
| profiles_blogs          | 13,665			  |
| profiles_blogs_followed | 121,094			  |
+-------------------------+--------------------+

New tables:
1. states_profiles
+-------------+--------------+------+-----+---------+-------+
| Field       | Type         | Null | Key | Default | Extra |
+-------------+--------------+------+-----+---------+-------+
| profile_url | varchar(100) | NO   |     | NULL    |       |
| state       | text         | NO   |     | NULL    |       |
+-------------+--------------+------+-----+---------+-------+
2. team_blogs
+----------+--------------+------+-----+---------+-------+
| Field    | Type         | Null | Key | Default | Extra |
+----------+--------------+------+-----+---------+-------+
| blog_url | varchar(100) | NO   |     |         |       |
+----------+--------------+------+-----+---------+-------+
3. state_profile_blog_post_content
+--------------+--------------+------+-----+---------+-------+
| Field        | Type         | Null | Key | Default | Extra |
+--------------+--------------+------+-----+---------+-------+
| state        | text         | NO   |     | NULL    |       |
| profile_url  | varchar(100) | NO   |     | NULL    |       |
| blog_url     | varchar(100) | NO   |     |         |       |
| post_url     | varchar(500) | NO   |     |         |       |
| post_content | longtext     | NO   |     | NULL    |       |
+--------------+--------------+------+-----+---------+-------+
*/
select 'Begin: drop tables' as '';
DROP TABLE states_profiles;
DROP TABLE team_blogs;
DROP TABLE team_posts;
DROP TABLE state_profile_post_content;
select 'End: drop tables' as '';

select 'Begin: create table states_profiles' as '';
create table states_profiles as select state, url from profiles where state is not null and country = 'United States';

ALTER TABLE states_profiles CHANGE url profile_url varchar(100);
ALTER TABLE states_profiles MODIFY profile_url varchar(100) NOT NULL; -- should be no warning
ALTER TABLE states_profiles MODIFY state text NOT NULL; -- should be no warning
select 'End: create table states_profiles' as '';

/*
create table state_profile_blog_post_content as
select SP.state, SP.profile_url, PB.blog_url, BP.post_url
from states_profiles SP, profiles_blogs PB, blogs_posts BP
where
	SP.profile_url = PB.profile_url and
	PB.blog_url = BP.blog_url;
*/

select 'Begin: create table team_blogs' as '';
create table team_blogs as select blog_url from profiles_blogs group by blog_url having count(*) > 1; -- 21 rows affected
select 'End: create table team_blogs' as '';

/*
delete from state_profile_blog_post_content where blog_url in (select blog_url from team_blogs); -- 23130 rows affected

ALTER TABLE state_profile_blog_post_content ADD post_content longtext;

UPDATE state_profile_blog_post_content
INNER JOIN posts ON state_profile_blog_post_content.post_url = posts.url
SET state_profile_blog_post_content.post_content = posts.content;

ALTER TABLE state_profile_blog_post_content MODIFY post_content longtext NOT NULL; -- should be no warning
*/

-- alternative solution

select 'Begin: create table team_posts' as '';
create table team_posts as
select BP.post_url
from team_blogs TB, blogs_posts BP
where TB.blog_url = BP.blog_url;
select 'End: create table team_posts' as '';


select 'Begin: create table state_profile_post_content' as '';
create table state_profile_post_content as
select SP.state, SP.profile_url, P.url, P.content 
from states_profiles SP, posts P
where
	SP.profile_url = P.author_url and
	P.url not in (select post_url from team_posts);

select 'End: create table state_profile_post_content' as '';
