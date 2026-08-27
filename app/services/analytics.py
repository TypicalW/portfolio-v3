import os

from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)


# =========================
# VIEWS
# =========================

def record_view():
    response = (
        supabase
        .table("analytics_events")
        .insert({
            "event_type": "view",
        })
        .execute()
    )

    return response


def get_total_views():
    response = (
        supabase
        .table("analytics_events")
        .select("id", count="exact")
        .eq("event_type", "view")
        .execute()
    )

    return response.count or 0


# =========================
# CLICKS
# =========================

def record_click(visitor_id):
    response = (
        supabase
        .table("analytics_events")
        .insert({
            "event_type": "click",
            "visitor_id": visitor_id,
        })
        .execute()
    )

    return response


def get_total_clicks():
    response = (
        supabase
        .table("analytics_events")
        .select("id", count="exact")
        .eq("event_type", "click")
        .execute()
    )

    return response.count or 0


def get_user_clicks(visitor_id):
    response = (
        supabase
        .table("analytics_events")
        .select("id", count="exact")
        .eq("event_type", "click")
        .eq("visitor_id", visitor_id)
        .execute()
    )

    return response.count or 0


def record_time(visitor_id, duration_seconds):
    response = (
        supabase
        .table("analytics_events")
        .insert({
            "event_type": "time",
            "visitor_id": visitor_id,
            "duration_seconds": duration_seconds,
        })
        .execute()
    )

    return response


def get_user_time(visitor_id):
    response = (
        supabase
        .table("analytics_events")
        .select("duration_seconds")
        .eq("event_type", "time")
        .eq("visitor_id", visitor_id)
        .execute()
    )

    return sum(
        event["duration_seconds"]
        for event in response.data
        if event["duration_seconds"] is not None
    )