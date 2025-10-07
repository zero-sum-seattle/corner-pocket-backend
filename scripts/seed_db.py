#!/usr/bin/env python3
"""Seed the database with sample data for development.

Usage:
    poetry run python scripts/seed_db.py
"""
from datetime import datetime, timedelta
from corner_pocket_backend.core.db import SessionLocal
from corner_pocket_backend.models import (
    User, Match, Game, Approval,
    GameType, MatchStatus, ApprovalStatus
)


def seed_database():
    """Create sample users, matches, games, and approvals."""
    db = SessionLocal()
    
    try:
        print("🎱 Seeding Corner Pocket database...")
        
        # Create users
        print("\n👤 Creating users...")
        fast_eddie = User(
            handle="fast_eddie",
            display_name="Fast Eddie Felson",
            email="eddie@poolhall.com",
            password_hash=None,  # TODO: Add password hashing
        )
        minnesota_fats = User(
            handle="minnesota_fats",
            display_name="Minnesota Fats",
            email="fats@poolhall.com",
            password_hash=None,
        )
        vincent = User(
            handle="vincent",
            display_name="Vincent Lauria",
            email="vincent@poolhall.com",
            password_hash=None,
        )
        
        db.add_all([fast_eddie, minnesota_fats, vincent])
        db.commit()
        print(f"   ✓ Created {fast_eddie.display_name} (@{fast_eddie.handle})")
        print(f"   ✓ Created {minnesota_fats.display_name} (@{minnesota_fats.handle})")
        print(f"   ✓ Created {vincent.display_name} (@{vincent.handle})")
        
        # Create matches
        print("\n🎯 Creating matches...")
        
        # Match 1: Completed match between Eddie and Fats
        match1 = Match(
            creator_id=fast_eddie.id,
            opponent_id=minnesota_fats.id,
            game_type=GameType.NINE_BALL,
            race_to=5,
            status=MatchStatus.APPROVED,
        )
        db.add(match1)
        db.commit()
        
        # Add games to match 1
        games1 = [
            Game(match_id=match1.id, game_type=GameType.NINE_BALL, winner_user_id=fast_eddie.id, loser_user_id=minnesota_fats.id, frame_number=1),
            Game(match_id=match1.id, game_type=GameType.NINE_BALL, winner_user_id=minnesota_fats.id, loser_user_id=fast_eddie.id, frame_number=2),
            Game(match_id=match1.id, game_type=GameType.NINE_BALL, winner_user_id=fast_eddie.id, loser_user_id=minnesota_fats.id, frame_number=3),
            Game(match_id=match1.id, game_type=GameType.NINE_BALL, winner_user_id=fast_eddie.id, loser_user_id=minnesota_fats.id, frame_number=4),
            Game(match_id=match1.id, game_type=GameType.NINE_BALL, winner_user_id=minnesota_fats.id, loser_user_id=fast_eddie.id, frame_number=5),
            Game(match_id=match1.id, game_type=GameType.NINE_BALL, winner_user_id=fast_eddie.id, loser_user_id=minnesota_fats.id, frame_number=6),
        ]
        db.add_all(games1)
        db.commit()
        
        # Create approval for match 1
        approval1 = Approval(
            match_id=match1.id,
            approver_user_id=minnesota_fats.id,
            status=ApprovalStatus.APPROVED,
            note="Good game! You got lucky this time.",
        )
        db.add(approval1)
        db.commit()
        print(f"   ✓ Match 1: {fast_eddie.display_name} vs {minnesota_fats.display_name} (APPROVED, 9-ball race to 5)")
        
        # Match 2: Pending match between Eddie and Vincent
        match2 = Match(
            creator_id=fast_eddie.id,
            opponent_id=vincent.id,
            game_type=GameType.EIGHT_BALL,
            race_to=7,
            status=MatchStatus.PENDING,
        )
        db.add(match2)
        db.commit()
        
        # Add a few games to match 2
        games2 = [
            Game(match_id=match2.id, game_type=GameType.EIGHT_BALL, winner_user_id=fast_eddie.id, loser_user_id=vincent.id, frame_number=1),
            Game(match_id=match2.id, game_type=GameType.EIGHT_BALL, winner_user_id=vincent.id, loser_user_id=fast_eddie.id, frame_number=2),
            Game(match_id=match2.id, game_type=GameType.EIGHT_BALL, winner_user_id=fast_eddie.id, loser_user_id=vincent.id, frame_number=3),
        ]
        db.add_all(games2)
        db.commit()
        print(f"   ✓ Match 2: {fast_eddie.display_name} vs {vincent.display_name} (PENDING, 8-ball race to 7)")
        
        # Match 3: Another approved match
        match3 = Match(
            creator_id=vincent.id,
            opponent_id=minnesota_fats.id,
            game_type=GameType.TEN_BALL,
            race_to=3,
            status=MatchStatus.APPROVED,
        )
        db.add(match3)
        db.commit()
        
        games3 = [
            Game(match_id=match3.id, game_type=GameType.TEN_BALL, winner_user_id=minnesota_fats.id, loser_user_id=vincent.id, frame_number=1),
            Game(match_id=match3.id, game_type=GameType.TEN_BALL, winner_user_id=minnesota_fats.id, loser_user_id=vincent.id, frame_number=2),
            Game(match_id=match3.id, game_type=GameType.TEN_BALL, winner_user_id=vincent.id, loser_user_id=minnesota_fats.id, frame_number=3),
            Game(match_id=match3.id, game_type=GameType.TEN_BALL, winner_user_id=minnesota_fats.id, loser_user_id=vincent.id, frame_number=4),
        ]
        db.add_all(games3)
        db.commit()
        
        approval3 = Approval(
            match_id=match3.id,
            approver_user_id=minnesota_fats.id,
            status=ApprovalStatus.APPROVED,
            note="Not bad for a rookie!",
        )
        db.add(approval3)
        db.commit()
        print(f"   ✓ Match 3: {vincent.display_name} vs {minnesota_fats.display_name} (APPROVED, 10-ball race to 3)")
        
        print("\n✅ Database seeded successfully!")
        print("\n📊 Summary:")
        print(f"   • {db.query(User).count()} users")
        print(f"   • {db.query(Match).count()} matches")
        print(f"   • {db.query(Game).count()} games")
        print(f"   • {db.query(Approval).count()} approvals")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()


