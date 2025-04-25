# GERBET & CO

![Website Mock Up](readme/gerbet_and_co_mockup.png)

## Table of Contents

-   [Project Description](#project-description)
    -   [Purpose](#purpose)
    -   [User Demographics](#user-demographics)
-   [Business Model & Marketing](#business-model--marketing)
    -   [E-commerce Business Model: Gerbet & Co.](#e-commerce-business-model-gerbet--co)
    -   [Marketing Strategies](#marketing-strategies)
-   [UX design](#ux-design)
    -   [User Stories](#user-stories)
    -   [Wireframes](#wireframes)
    -   [Flowcharts](#flowcharts)
    -   [Key Design Decisions](#key-design-decisions)
        -   [Imagery](#imagery)
        -   [Color Scheme](#colour-scheme)
        -   [Typography](#typography)
        -   [Interactive Elements](#interactive-elements)
-   [Agile Methodology](#agile-methodology)
-   [Features](#features)
    -   [Existing Features](#existing-features)
    -   [Future Features](#future-features)
-   [Technologies](#technologies)
-   [Deployment](#deployment)
    -   [How to clone](#how-to-clone)
    -   [Neon PostgeSQL Database](#neon-postgesql-database)
    -   [Cloudinary API](#cloudinary-api)
    -   [Google API](#google-api)
    -   [Heroku](#heroku)
-   [Testing](#testing)
    -   [Responsivness Testing](#responsivness-testing)
    -   [Browser compatibility Testing](#browser-compatibility-testing)
    -   [User Stories / Features Testing](#user-stories--features-testing)
    -   [Code Validation](#code-validation)
    -   [Performance](#performance)
    -   [Known Issues](#known-issues)
-   [Credits](#credits)
    -   [Media](#media)
    -   [Code](#code)
-   [Acknowledgments](#acknowledgments)

[Back to top](#table-of-contents)

---

# Project Description

Gerbet & Co. is a full-stack e-commerce platform offering luxury handmade French-style macarons and curated tea blends. Built using Django, HTMX, Bootstrap 5 CSS, and PostgreSQL (Neon), the site delivers an elegant, user-friendly shopping experience with a focus on small-batch quality, storytelling, and gift-ready presentation.

The platform includes features such as product filtering, real-time cart updates, Stripe integration, customer account management, and admin-controlled product management. Each product page highlights flavor notes, pairing suggestions, and compelling visuals to support both browsing and buying decisions.

## Purpose

The project was developed as part of a full-stack portfolio to demonstrate strong back-end and front-end integration, dynamic data handling, and thoughtful UX for a niche market. It combines technical precision with a brand-forward design to reflect the personal and artisanal nature of the products.

From a business perspective, the platform supports a direct-to-consumer (DTC) model, empowering small-scale sellers to manage inventory, communicate brand values, and build customer loyalty without relying on third-party marketplaces.

## User Demographics

This site is designed primarily for:

-   Individuals seeking premium, handmade sweets or elegant gift items
-   Tea enthusiasts interested in curated pairings and boutique blends
-   Event planners, couples, and businesses looking for customized favors and treats
-   Customers within Ireland and the broader EU who value artisanal quality and beautiful presentation
-   Mobile and desktop users alike, with responsive design to support browsing and purchasing across devices

[Back to top](#table-of-contents)

---

# Business Model & Marketing

## E-commerce Business Model: Gerbet & Co.

Gerbet & Co. is a small, independent e-commerce business specializing in high-quality French-style macarons and thoughtfully curated tea blends. Rooted in traditional baking techniques and personal craftsmanship, each batch is made in limited quantities with an emphasis on precision, quality, and care.

The shop follows a direct-to-consumer (DTC) model, selling exclusively through its own online platform. This approach allows full control over product quality, packaging, and customer experience. Orders are placed directly through the website and fulfilled from a small-scale production kitchen, with delivery available across Ireland and Europe. Many products are made to order or offered in small seasonal batches to maintain freshness and exclusivity.

## Marketing Strategies

1. Product-First Storytelling
   Gerbet & Co. emphasizes high-quality ingredients, artisanal techniques, and a meaningful founder story — all of which are showcased in the About page. Visual and written content is crafted to create an emotional connection with customers, presenting each order as a joyful, gift-worthy experience.

2. Visual Social Media Presence
   The brand maintains a strong presence on Instagram and Pinterest, highlighting behind-the-scenes baking, seasonal launches, and packaging rituals. User-generated content (UGC) and customer testimonials are featured through styled photography and story reposts to build trust and engagement.

3. Email Marketing with a Personal Touch
   Subscribers receive curated emails including seasonal collection announcements, restock alerts, and macaron-tea pairing ideas. Limited batch drops and early access to new products help create urgency and community around the brand.

4. Niche Positioning
   Marketing efforts are tailored to specific audiences such as gift buyers, tea enthusiasts, and event planners. Customizable options for weddings, birthdays, and corporate gifts allow Gerbet & Co. to stand out in premium gifting categories.

5. Local SEO & Community Involvement
   To strengthen local visibility, keywords like “handmade macarons Ireland” and “luxury treats Dublin” are used throughout the site. The brand also explores partnerships with local businesses and participates in community events and pop-ups to build grassroots awareness.

6. Focus on the Gifting Experience
   Every product is packaged with care, using minimal yet elegant design. Optional handwritten notes and curated gift sets are offered, making the experience ideal for occasions like anniversaries, holidays, and thank-you gifts.

[Back to top](#table-of-contents)

---

# UX Design

## User Stories

The list of user stories can be found in [Gerbet & Co GitHub project](https://github.com/users/tayapro/projects/5).

## Wireframes

### Landing page

<img src="readme/Landing_page_wireframe.png" width="400" alt="Landing_page_wireframe.png">

### Products page

<img src="readme/Products_page_wireframe.png" width="400" alt="Products_page_wireframe">

### Product view page

<img src="readme/Product_page_wireframe.png" width="400" alt="Product_page_wireframe">

### Account page

<img src="readme/Account_page_wireframe.png" width="400" alt="Account_page_wireframe">

### Account profile page

<img src="readme/Account_profile_page_wireframe.png" width="400" alt="Account_profile_page_wireframe">

### Accout profile edit page

<img src="readme/Account_profile_edit_page_wireframe.png" width="400" alt="Account_profile_edit_page_wireframe">

### Account profile password update page

<img src="readme/Account_profile_password_update_page_wireframe.png" width="400" alt="Account_profile_password_update_page_wireframe">

### Account address list page

<img src="readme/Account_address_list_page_wireframe.png" width="400" alt="Account_address_list_page_wireframe">

### Account create/update address pages

<img src="readme/Account_address_create_update_page_wireframe.png width="400" alt="Account_address_create_update_page_wireframe">

### Account delete page

<img src="readme/Account_address_delete_page_wireframe.png" width="400" alt="Account_address_delete_page_wireframe">

### Account order list page

<img src="readme/Account_orders_list_page_wireframe.png" width="400" alt="Account_orders_list_page_wireframe">

### Account order view page

<img src="readme/Account_order_view_page_wireframe.png" width="400" alt="Account_order_view_page_wireframe">

### Bag page

<img src="readme/Bag_view_page_wireframe.png" width="400" alt="Bag_view_page_wireframe">

### Checkout page

<img src="readme/Checkout_page_wireframe.png" width="400" alt="Checkout_page_wireframe">

### Checkout success page

<img src="readme/Checkout_success_page_wireframe.png" width="400" alt="Checkout_success_page_wireframe">

### Login page

<img src="readme/Login_page_wireframe.png" width="400" alt="Login_page_wireframe">

### Register page

<img src="readme/Register_page_wireframe.png" width="400" alt="Register_page_wireframe">

### Logout page

<img src="readme/Logout_page_wireframe.png" width="400" alt="Logout_page_wireframe">

### Forget password page

<img src="readme/Forget_password_page_wireframe.png" width="400" alt="Forget_password_page_wireframe">

### Error pages

<img src="readme/Error_pages_wireframe.png" width="400" alt="Error_pages_wireframe">

## Flowcharts

Diagrams.net (Draw.io) was used to create the Entity Relationship Diagram (ERD) for the Gerbet & Co project.
It provided a clear and accessible way to map out model relationships and plan the database structure effectively.

<img src="readme/gerbetco_flowchart.png" width="700" alt="gerbet flowchart">

[Back to top](#table-of-contents)

---

# Agile Methodology

## GitHub Projects

GitHub Projects was utilized to manage this project following Agile principles. While not a dedicated project management platform, it proved effective when paired with labels, issues, and project boards to organize tasks, track progress, and maintain workflow transparency.

The link to the Gerbet & Co board can be found [here](https://github.com/users/tayapro/projects/5).

Using GitHub Projects, user stories, issues, and tasks were organized and tracked weekly via a simple Kanban board. This approach provided clear visibility into progress and allowed for easy updates and adjustments throughout the development process.

<img src="readme/kanban_board.png" width="600" alt="Kanban board">

The **MoSCoW prioritization method** was used alongside custom GitHub project labels to effectively organize tasks. This approach ensured that the most critical features were addressed first, helping to maintain focus and make the best use of the available time.

## Milestones

Milestones were used to group related user stories, helping to structure the development process and maintain focus.

<img src="readme/milestones.png" width="600" alt="milestones">

This approach supported timely delivery by aligning tasks with priorities and deadlines, ensuring that key features were completed in the right order.

## MoSCoW Prioritization

Before implementation began, high-level Epics were broken down into smaller, actionable user stories. This allowed for the application of the MoSCoW prioritization method within the GitHub Issues tab, using custom labels to categorize and manage task importance.

The MoSCoW method was used to group tasks as follows:

-   **Must Have** – Essential features required for the core functionality and successful delivery.
-   **Should Have** – High-value tasks that enhance the product but aren’t critical for launch.
-   **Could Have** – Nice-to-have features that provide added value but can be deferred.
-   **Won’t Have** – Tasks intentionally excluded from the current development cycle.

This structured approach ensured that key features were delivered first, while still making space for future
enhancements to improve the user experience in later iterations.

[Back to top](#table-of-contents)

---
