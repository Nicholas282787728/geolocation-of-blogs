-- 
-- This script creates 3 new tables in addition to 6 original tables.
-- 
-- Original tables:
-- +-------------------------+--------------------+
-- | Tables_in_myblogs       | Number of rows 	  |
-- +-------------------------+--------------------+
-- | blogs                   | 12,562			  |
-- | blogs_posts             | 2,303,343		  |
-- | posts                   | 2,303,755		  |
-- | profiles                | 6,750			  |
-- | profiles_blogs          | 13,665			  |
-- | profiles_blogs_followed | 121,094			  |
-- +-------------------------+--------------------+
-- 
-- New tables:
-- 1. states_profiles
-- +-------------+--------------+------+-----+---------+-------+
-- | Field       | Type         | Null | Key | Default | Extra |
-- +-------------+--------------+------+-----+---------+-------+
-- | profile_url | varchar(100) | NO   |     | NULL    |       |
-- | state       | text         | NO   |     | NULL    |       |
-- +-------------+--------------+------+-----+---------+-------+
-- 2. team_blogs
-- +----------+--------------+------+-----+---------+-------+
-- | Field    | Type         | Null | Key | Default | Extra |
-- +----------+--------------+------+-----+---------+-------+
-- | blog_url | varchar(100) | NO   |     |         |       |
-- +----------+--------------+------+-----+---------+-------+
-- 3. state_profile_blog_post_content
-- +--------------+--------------+------+-----+---------+-------+
-- | Field        | Type         | Null | Key | Default | Extra |
-- +--------------+--------------+------+-----+---------+-------+
-- | state        | text         | NO   |     | NULL    |       |
-- | profile_url  | varchar(100) | NO   |     | NULL    |       |
-- | blog_url     | varchar(100) | NO   |     |         |       |
-- | post_url     | varchar(500) | NO   |     |         |       |
-- | post_content | longtext     | NO   |     | NULL    |       |
-- +--------------+--------------+------+-----+---------+-------+

create table states_profiles as select state, url from profiles where state is not null and country = 'United States';


ALTER TABLE states_profiles CHANGE url profile_url;
ALTER TABLE states_profiles MODIFY profile_url varchar(100) NOT NULL;
ALTER TABLE states_profiles MODIFY state text NOT NULL;


create table state_profile_blog_post_content as
select SP.state, SP.profile_url, PB.blog_url, BP.post_url
from states_profiles SP, profiles_blogs PB, blogs_posts BP
where
	SP.profile_url = PB.profile_url and
	PB.blog_url = BP.blog_url;


create table team_blogs as select blog_url from profiles_blogs group by blog_url having count(*) > 1; -- 21 rows affected
delete from state_profile_blog_post_content where blog_url in (select blog_url from team_blogs); -- 23130 rows affected



ALTER TABLE state_profile_blog_post_content ADD post_content longtext;

UPDATE state_profile_blog_post_content
INNER JOIN posts ON state_profile_blog_post_content.post_url = posts.url
SET state_profile_blog_post_content.post_content = posts.content;

ALTER TABLE state_profile_blog_post_content MODIFY post_content longtext NOT NULL;

