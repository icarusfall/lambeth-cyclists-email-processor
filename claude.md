# Lambeth Cyclists Project Management System

## The Problem

Lambeth Cyclists is a real-world cycling advocacy and support group in South London, UK, part of the London Cycling Campaign charity. The organization is currently running on skeleton staff operationally and needs better tooling to enable effective project management and response to consultations, traffic orders, and infrastructure projects.

**What started as:** A smart way to file and summarize emails about Lambeth cycling-related topics (consultations, traffic orders, infrastructure projects, events).

**What it became:** A comprehensive Notion-based project management system with Railway-hosted automation that:
- Automatically processes incoming emails
- Extracts structured data with AI
- Geocodes locations
- Generates meeting agendas
- Sends automated reminders
- Manages three interconnected databases (Items, Projects, Meetings)

**Goal:** Enable Charlie (chair) to focus more effectively on Lambeth Cyclists work by automating administrative tasks and providing better project oversight, making it easier to recruit and onboard volunteers.

---

## Organization Context

**Lambeth Cyclists**
- Branch of London Cycling Campaign (LCC) charity
- Focus area: London Borough of Lambeth, South London
- Current team: Charlie Ullman (chair) + Colin (committee member)
- Status: Skeleton staff, actively looking to resource up
- Activities:
  - Responding to TfL and Lambeth Council consultations
  - Advocating for better cycling infrastructure
  - Organizing social rides
  - Attending bi-monthly committee meetings (hybrid format)
  - Supporting London Cycling Campaign

**Communications:**
- Gmail: Incoming emails about consultations, traffic orders, projects
- WhatsApp: Committee coordination (mainly Charlie + Colin)
- Google Groups: Public mailing list for interested cyclists
- LCC messaging system: ~1000+ LCC members in Lambeth borough

---

## System Architecture

### Core Components

**Frontend (User-Facing):**
- **Notion** - Three databases for project management:
  - **Items Database**: Reactive, email-triggered entries (consultations, traffic orders, infrastructure projects)
  - **Projects Database**: Strategic, long-term initiatives (e.g., A23 Brixton Hill crossing campaign)
  - **Meetings Database**: Committee meetings with auto-generated agendas

**Backend (Railway):**
- Python application running 24/7 on Railway
- Processes emails every 5 minutes
- Checks for meetings every hour
- Sends email alerts and reminders

**APIs & Services:**
- Gmail API: Email monitoring
- Claude API (Anthropic): AI analysis and agenda generation
- Notion API: Database management
- Google Maps API: Location geocoding
- Google Drive API: Attachment storage
- SMTP: Email notifications

---

## Current State (as of January 10, 2026)

### Deployment Status
✅ **Live and running on Railway** since January 10, 2026
- Email processing working successfully
- Geocoding enabled and functional
- Meeting agenda generation tested
- Email alerts configured for Charlie + Colin

### What's Working
- **Email Processing Pipeline** (Phases 1-7):
  - Gmail monitoring (every 5 minutes)
  - Attachment processing (PDFs, Word docs, images, Excel)
  - Claude AI analysis with vision capabilities
  - Location geocoding with Google Maps
  - Google Drive upload for attachments
  - Notion item creation with all fields populated
  - Duplicate detection
  - Relationship detection between items

- **Meeting Agenda Generation** (Phase 8):
  - Auto-detects meetings 1-2 days before date
  - Gathers new items since last meeting
  - Identifies items with approaching deadlines
  - Pulls active projects
  - Generates AI discussion prompts
  - Updates Notion with formatted agenda

- **Email Reminders & Alerts** (Phase 9):
  - Agenda generated notification
  - Daily "nag" emails if agenda not approved (during week before meeting)
  - "Meeting tomorrow" reminders
  - "Add minutes" reminders after meetings
  - Error alerts
  - Multi-recipient support (Charlie + Colin)

### Configuration
- **Gmail label**: "Lambeth Cycling Projects"
- **Email polling**: Every 5 minutes (300s)
- **Meeting checks**: Every hour (3600s)
- **Alert recipients**: charlie.ullman@gmail.com, colin@penning.org.uk
- **Railway**: Python 3.12 environment

### Phases Completed
- ✅ Phases 1-7: Email processing pipeline
- ✅ Phase 8: Meeting agenda generation
- ✅ Phase 9: Email reminders and alerts
- ✅ Phase 12: Railway deployment

### Phases Deferred/Skipped
- Phase 10: Data migration (not needed - emails processed from scratch)
- Phase 11: Comprehensive testing (manual validation sufficient)

---

## Upcoming Events

**Next Committee Meeting:**
- Date: February 10, 2026, 19:00
- Format: Hybrid
- Location: Stockwell Centre, Morley College
- Agenda: Will auto-generate on February 8th
- Topics: Infrastructure updates, May council elections strategy, recruitment

---

## Technical Notes

### Fixed Issues
- **Python 3.12 Compatibility**: Fixed Anthropic/httpx version incompatibility
  - Updated `anthropic==0.45.0`
  - Added `httpx>=0.27.0`

### System Behavior
- Meetings: System checks hourly but only sends each type of reminder once (not hourly!)
- Duplicate detection: Emails with "processed" label are skipped
- Geocoding: Tested and working with Google Maps billing enabled
- Local dev: Python 3.10, works fine with updated requirements

### To Be Done
- **Phase 13**: Decommission Zapier (previous email automation solution)
  - Wait a week or two to confirm Railway system is stable
  - Then disable Zapier to save subscription cost

---

## Key People

**Charlie Ullman** (chair)
- Email: charlie.ullman@gmail.com
- Role: Chairs meetings, manages email processing, responds to consultations
- Focus: Wants to resource up the organization, needs better project management tools

**Colin**
- Email: colin@penning.org.uk
- Role: Committee member
- Status: Has Notion workspace access

---

## Notion Database Structure

### Items Database
Reactive, email-triggered entries for:
- Consultations (e.g., cycle lane proposals)
- Traffic orders (e.g., parking removal)
- Infrastructure projects (e.g., new cycle lane installations)
- Events (e.g., car-free days)

**Key Fields:**
- Title, Summary, Date Received
- Consultation Deadline, Action Required
- Project Type (consultation, traffic_order, infrastructure, event, etc.)
- Tags (multi-select)
- Locations (with geocoded coordinates)
- AI Key Points
- Priority
- Attachment URLs
- Related Project (relation)
- Email Details (sender, message ID, Gmail URL)

### Projects Database
Strategic, long-term initiatives:
- Multi-email campaigns
- Ongoing advocacy efforts
- Infrastructure project tracking

**Key Fields:**
- Title, Summary
- Status (active, planned, completed, on_hold)
- Priority
- Primary Locations
- Current Status (text updates)
- Start/Target Completion Dates
- Related Items (relation)

### Meetings Database
Committee meetings with automation:

**Key Fields:**
- Meeting Title, Meeting Date
- Meeting Type (regular_committee, emergency, planning, special)
- Meeting Format (Hybrid, Online Only, In-person)
- Location, Zoom Link
- Auto-Generated Agenda
- Manual Agenda Items
- Agenda Generation Status (pending, generated, approved, published)
- Meeting Notes, Decisions Made, Action Items
- Items to Discuss (relation)
- Projects to Review (relation)

---

## Standard Meeting Introduction

Used in auto-generated agendas:

> "Hello and welcome to the meeting for Lambeth Cyclists - we are the Lambeth branch of the charity London Cycling Campaign. Whether you are a member of LCC or not, you are more than welcome to join and give your thoughts. We are interested in basically anyone who wants to make conditions in Lambeth better for cyclists of all ages.
>
> We try to be studiously apolitical, but part of our role is often as a consultee on TfL or Lambeth Council road or infrastructure plans. We also organise social rides when we can, and we support the central London Cycling Campaign as we can."

---

## Development History

**Initial Problem:**
- Manual email processing was time-consuming
- Zapier only handled 1 attachment per email
- No structured project management
- Meeting agendas created manually
- Easy to forget about deadlines

**Solution Built:**
- Comprehensive automation pipeline
- AI-powered email analysis with vision
- Three-database Notion structure
- Automated meeting agenda generation
- Email reminder system with "relentless nagging" for meeting admin

**Outcome:**
- 24/7 automated email processing
- Smart project management via Notion
- Reduced manual administrative burden
- Better organized for volunteer recruitment
- Charlie can focus more on advocacy work

---

## Cost & Maintenance

**Monthly Costs:**
- Railway: $0 (within free tier $5 credit/month)
- Claude API: ~$2-5/month
- Google Maps API: $0 (within $200/month free credit)
- Gmail API: $0
- Notion: $0

**Total: ~$2-5/month** (replacing Zapier subscription)

**Monitoring:**
- Railway logs: https://railway.app/
- Claude API usage: https://console.anthropic.com/
- Google Cloud Console: https://console.cloud.google.com/

---

## Future Considerations

**Recruitment Focus:**
- System designed to make Lambeth Cyclists more manageable
- Clearer project tracking helps onboard volunteers
- Automated admin reduces barrier to participation
- Notion workspace can be shared with new committee members

**Potential Enhancements:**
- Public-facing website (currently just Notion + email automation)
- More sophisticated project prioritization
- Integration with LCC central systems
- Social media automation
- Event management features

---

## Files & Documentation

**Key Documentation:**
- `GETTING_STARTED.md`: Initial setup guide
- `OAUTH_SETUP_GUIDE.md`: Google OAuth configuration
- `NOTION_SETUP_GUIDE.md`: Notion database setup
- `EMAIL_ALERTS_SETUP.md`: SMTP/Gmail app password setup
- `RAILWAY_DEPLOYMENT.md`: Railway deployment guide
- `PHASE_8_9_COMPLETE.md`: Meeting features testing guide

**Test Scripts:**
- `test_connections.py`: Verify API connections
- `test_email_alerts.py`: Test SMTP email sending
- `test_geocoding.py`: Test Google Maps geocoding

---

## Important Links

**Production:**
- Railway: https://railway.app/
- GitHub: https://github.com/icarusfall/lambeth-cyclists-email-processor

**APIs:**
- Claude Console: https://console.anthropic.com/
- Google Cloud Console: https://console.cloud.google.com/
- Notion Integrations: https://www.notion.so/my-integrations

**Organization:**
- London Cycling Campaign: https://lcc.org.uk/
- Lambeth Cyclists (need to add website when available)
