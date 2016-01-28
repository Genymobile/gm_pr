--
-- Copyright 2016 Genymobile
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--     http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.


-- The commands in this file are optional.

-- If you wish to configure the projects and repositories to be
-- created when the docker image is run, instead of manually creating
-- them using the admin interface, uncomment and adapt the statements below.
-- The examples below are for repositories in the Google account
-- (https://github.com/google).

/* delete any projects/repos previously configured */
-- delete from gm_pr_project;
-- delete from gm_pr_repo;
-- delete from gm_pr_repo_projects;

/* create projects */
-- insert into gm_pr_project VALUES(1, "Material design repos");
-- insert into gm_pr_project VALUES(2, "GCM repos");

/* add repos for the projects */
-- insert into gm_pr_repo VALUES(1, "material-design-lite");
-- insert into gm_pr_repo VALUES(2, "material-design-icons");
-- insert into gm_pr_repo VALUES(3, "gcm");
-- insert into gm_pr_repo VALUES(4, "go-gcm");

/* link the repos to the projects */
-- insert into gm_pr_repo_projects (repo_id, project_id) VALUES(1,1);
-- insert into gm_pr_repo_projects (repo_id, project_id) VALUES(2,1);
-- insert into gm_pr_repo_projects (repo_id, project_id) VALUES(3,2);
-- insert into gm_pr_repo_projects (repo_id, project_id) VALUES(4,2);
