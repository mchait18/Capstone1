-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- Link to schema: https://app.quickdatabasediagrams.com/#/d/kQKlMU
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.

-- Modify this code to update the DB schema diagram.
-- To reset the sample schema, replace everything with
-- two dots ('..' - without quotes).

CREATE TABLE "meal_plan" (
    "id" int   NOT NULL,
    "user_id" int   NOT NULL,
    "start_date" date   NOT NULL,
    "end_date" date   NOT NULL,
    CONSTRAINT "pk_meal_plan" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "users" (
    "id" int   NOT NULL,
    "email" string   NOT NULL,
    "username" string   NOT NULL,
    "password" text   NOT NULL,
    CONSTRAINT "pk_users" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "days" (
    "id" int   NOT NULL,
    "name" text   NOT NULL,
    "meal_plan_id" int   NOT NULL,
    CONSTRAINT "pk_days" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "recipes" (
    "id" int   NOT NULL,
    "text" string   NOT NULL,
    "user_id" int   NOT NULL,
    CONSTRAINT "pk_recipes" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "recipe_day" (
    "id" int   NOT NULL,
    "day_id" int   NOT NULL,
    "recipe_id" int   NOT NULL,
    CONSTRAINT "pk_recipe_day" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "shopping_list" (
    "id" int   NOT NULL,
    "user_id" int   NOT NULL,
    CONSTRAINT "pk_shopping_list" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "grocery_item" (
    "id" int   NOT NULL,
    "name" text   NOT NULL,
    "amount" text   NOT NULL,
    "shopping_list_id" int   NOT NULL,
    "recipe_id" int   NOT NULL,
    CONSTRAINT "pk_grocery_item" PRIMARY KEY (
        "id"
     )
);

ALTER TABLE "meal_plan" ADD CONSTRAINT "fk_meal_plan_user_id" FOREIGN KEY("user_id")
REFERENCES "users" ("id");

ALTER TABLE "days" ADD CONSTRAINT "fk_days_meal_plan_id" FOREIGN KEY("meal_plan_id")
REFERENCES "meal_plan" ("id");

ALTER TABLE "recipes" ADD CONSTRAINT "fk_recipes_user_id" FOREIGN KEY("user_id")
REFERENCES "users" ("id");

ALTER TABLE "recipe_day" ADD CONSTRAINT "fk_recipe_day_day_id" FOREIGN KEY("day_id")
REFERENCES "days" ("id");

ALTER TABLE "recipe_day" ADD CONSTRAINT "fk_recipe_day_recipe_id" FOREIGN KEY("recipe_id")
REFERENCES "recipes" ("id");

ALTER TABLE "shopping_list" ADD CONSTRAINT "fk_shopping_list_user_id" FOREIGN KEY("user_id")
REFERENCES "users" ("id");

ALTER TABLE "grocery_item" ADD CONSTRAINT "fk_grocery_item_shopping_list_id" FOREIGN KEY("shopping_list_id")
REFERENCES "shopping_list" ("id");

ALTER TABLE "grocery_item" ADD CONSTRAINT "fk_grocery_item_recipe_id" FOREIGN KEY("recipe_id")
REFERENCES "recipes" ("id");

