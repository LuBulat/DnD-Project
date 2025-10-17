from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import timedelta
import os
from werkzeug.utils import secure_filename
import uuid

# Inicijalizacija Flask aplikacije
app = Flask(__name__)

# Omogućavanje CORS-a
CORS(app, origins=["http://localhost:5173"], allow_headers=["Content-Type", "Authorization"], supports_credentials=True)

# Konfiguracija baze podataka i JWT-a
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/dnd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'neki_jako_tajni_kljuc'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Token traje 1 sat

# Konfiguracija za upload slika
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max veličina fajla

# Dozvoljene ekstenzije za slike
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Inicijalizacija modula
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Apstraktna baza za opise
class BaseDescription(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)

# Model za korisnike (user)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"
    
# Model za rase (race)
class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    ability_score_increase = db.Column(db.Text, nullable=False)
    speed = db.Column(db.Integer, nullable=False)
    traits = db.Column(db.Text, nullable=False)
    languages = db.Column(db.Text, nullable=False)
    proficiency = db.Column(db.String, nullable=True)

# Model za opis rase (race_description)
class RaceDescription(BaseDescription):
    __tablename__ = 'race_description'
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    race = db.relationship('Race', backref='descriptions', lazy=True)

# Model za podrase (subrace)
class Subrace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    ability_score_increase = db.Column(db.Text, nullable=False)
    traits = db.Column(db.Text, nullable=False)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    proficiency = db.Column(db.String, nullable=True)

    race = db.relationship('Race', backref=db.backref('subraces', lazy=True))

# Model za klase (class)
class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    hit_die = db.Column(db.Integer, nullable=False)
    saving_throws = db.Column(db.String(100), nullable=False)
    armor_proficiencies = db.Column(db.String(100), nullable=True)
    weapon_proficiencies = db.Column(db.String(100), nullable=True)
    tool_proficiencies = db.Column(db.String(100), nullable=True)
    skill_choices = db.Column(db.String(200), nullable=True)
    num_skills = db.Column(db.Integer, nullable=False)
    spellcasting = db.Column(db.Boolean, default=False)
    starting_equipment = db.Column(db.Text, nullable=False)
    class_features = db.Column(db.Text, nullable=False)
    spellcasting_ability = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Class {self.name}>"

# Model za opis klase (class_description)
class ClassDescription(BaseDescription):
    __tablename__ = 'class_description'
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    class_ = db.relationship('Class', backref='descriptions', lazy=True)

#Model za spajanje tabela klasa i magija (class_spell)
class ClassSpell(db.Model):
    __tablename__ = 'class_spell'
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), primary_key=True)
    spell_id = db.Column(db.Integer, db.ForeignKey('spell.spell_id'), primary_key=True)

# Model za magije (spells)
class Spell(db.Model):
    __tablename__ = 'spell'

    spell_id = db.Column(db.Integer, primary_key=True)
    spell_name = db.Column(db.String(100), nullable=False)
    spell_level = db.Column(db.String(50))
    spell_type = db.Column(db.String(100))
    casting_time = db.Column(db.String(100))
    spell_range = db.Column(db.String(100))
    components = db.Column(db.String(100))
    duration = db.Column(db.String(100))
    description = db.Column(db.Text)
    higher_levels = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.spell_id,
            'name': self.spell_name
        }

    def to_full_dict(self):
        return {
            'id': self.spell_id,
            'name': self.spell_name,
            'description': self.description
        }

# Model za pozadine (backgrounds)
class Background(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    skill_proficiencies = db.Column(db.String(200), nullable=False)
    tool_proficiencies = db.Column(db.String(200), nullable=True)
    starting_equipment = db.Column(db.Text, nullable=False)
    starting_gold = db.Column(db.Integer, default=0)
    features = db.Column(db.Text, nullable=False)
    languages = db.Column(db.String(200), nullable=True)
    personality_trait = db.Column(db.Text, nullable=True)
    ideal = db.Column(db.Text, nullable=True)
    bond = db.Column(db.Text, nullable=True)
    flaw = db.Column(db.Text, nullable=True)
    variant = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"<Background {self.name}>"

# Model za opis pozadine (backgrounds_description)
class BackgroundDescription(BaseDescription):
    __tablename__ = 'background_description'
    background_id = db.Column(db.Integer, db.ForeignKey('background.id'), nullable=False)
    background = db.relationship('Background', backref='descriptions', lazy=True)

# Model za karaktere (character)
class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    player_name = db.Column(db.String(255))
    char_class = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, default=1)
    background = db.Column(db.String(100))
    background_variant = db.Column(db.String(100))
    race = db.Column(db.String(50), nullable=False)
    subrace = db.Column(db.String(50))
    alignment = db.Column(db.String(50))
    experience_points = db.Column(db.String(50))
    hit_die = db.Column(db.Integer)
    hit_dice = db.Column(db.Integer, default=1)
    
    # Polja za choices
    selectable_skills = db.Column(db.JSON)
    max_selectable_skills = db.Column(db.Integer, default=0)
    previous_race_bonus = db.Column(db.Integer, default=0)
    previous_class_choices = db.Column(db.Integer, default=0)
    previous_overlap_count = db.Column(db.Integer, default=0)
    
    # Ability scores
    strength_score = db.Column(db.Integer, default=10)
    dexterity_score = db.Column(db.Integer, default=10)
    constitution_score = db.Column(db.Integer, default=10)
    intelligence_score = db.Column(db.Integer, default=10)
    wisdom_score = db.Column(db.Integer, default=10)
    charisma_score = db.Column(db.Integer, default=10)
    
    # Base vrednosti za bojenje
    base_ability_scores = db.Column(db.JSON)
    base_race_scores = db.Column(db.JSON)
    pure_race_scores = db.Column(db.JSON)
    base_speed = db.Column(db.Integer, default=30)
    
    # Passive Wisdom Perception vrednosti
    passive_wisdom = db.Column(db.Integer, default=10)
    passive_wisdom_base = db.Column(db.Integer, default=10)
    passive_wisdom_manual_modifier = db.Column(db.Integer, default=0)
    
    # Manualni modifikatori
    ac_manual_modifier = db.Column(db.Integer, default=0)
    spell_save_dc_manual_modifier = db.Column(db.Integer, default=0)
    spell_attack_bonus_manual_modifier = db.Column(db.Integer, default=0)
    initiative_modifier = db.Column(db.Integer, default=0)
    saving_throw_manual_modifiers = db.Column(db.JSON)
    skill_manual_modifiers = db.Column(db.JSON)
    
    # Saving throws (stored as JSON)
    saving_throws = db.Column(db.JSON)
    
    # Skills (stored as JSON)
    skills = db.Column(db.JSON)
    
    # Attack podaci (stored as JSON)
    attacks = db.Column(db.JSON)
    
    # Spell slots (stored as JSON)
    spell_slots = db.Column(db.JSON)
    
    # HP and combat stats
    hp_max = db.Column(db.Integer, default=0)
    hp_current = db.Column(db.Integer, default=0)
    hp_temp = db.Column(db.Integer, default=0)
    hp_base = db.Column(db.Integer, default=0)
    ac = db.Column(db.Integer, default=10)
    initiative = db.Column(db.Integer, default=0)
    speed = db.Column(db.Integer, default=30)
    
    # Death saves (stored as JSON)
    death_saves = db.Column(db.JSON)
    
    # Currency
    currency_cp = db.Column(db.Integer, default=0)
    currency_sp = db.Column(db.Integer, default=0)
    currency_ep = db.Column(db.Integer, default=0)
    currency_gp = db.Column(db.Integer, default=0)
    currency_pp = db.Column(db.Integer, default=0)
    
    # Equipment and features
    equipment = db.Column(db.Text)
    race_features = db.Column(db.Text)
    class_features = db.Column(db.Text)
    race_proficiency = db.Column(db.Text)
    class_proficiency = db.Column(db.Text)
    background_features = db.Column(db.Text)
    armor = db.Column(db.String(50))
    has_shield = db.Column(db.Boolean, default=False)
    
    # Personality
    personality_traits = db.Column(db.Text)
    personality_ideals = db.Column(db.Text)
    personality_bonds = db.Column(db.Text)
    personality_flaws = db.Column(db.Text)
    
    # Proficiency and Inspiration
    proficiency_bonus = db.Column(db.Integer, default=2)
    prof_bonus_modifier = db.Column(db.Integer, default=0)
    inspiration_value = db.Column(db.Integer, default=0)
    
    # Physical characteristics
    age = db.Column(db.String(50))
    height = db.Column(db.String(50))
    weight = db.Column(db.String(50))
    eyes = db.Column(db.String(50))
    skin = db.Column(db.String(50))
    hair = db.Column(db.String(50))
    
    # Backstory and appearance
    backstory = db.Column(db.Text)
    allies = db.Column(db.Text)
    treasure = db.Column(db.Text)
    
    # Reference na slike (samo putanje)
    appearance_image_path = db.Column(db.String(255))
    symbol_image_path = db.Column(db.String(255))
    symbol_name = db.Column(db.String(255))
    
    # Spellcasting
    spellcasting_ability = db.Column(db.String(20))
    spellcasting_save_dc = db.Column(db.Integer, default=8)
    spellcasting_attack_bonus = db.Column(db.Integer, default=0)
    
    # Spells (stored as JSON arrays)
    cantrips = db.Column(db.JSON)
    level1_spells = db.Column(db.JSON)
    level2_spells = db.Column(db.JSON)
    level3_spells = db.Column(db.JSON)
    level4_spells = db.Column(db.JSON)
    level5_spells = db.Column(db.JSON)
    level6_spells = db.Column(db.JSON)
    level7_spells = db.Column(db.JSON)
    level8_spells = db.Column(db.JSON)
    level9_spells = db.Column(db.JSON)
    
    # User relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('characters', lazy=True))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f"<Character {self.name}>"

# Kreiranje tabela ako ne postoje
with app.app_context():
    db.create_all()

    # Provera da li tabela race već ima podatke
    if not Race.query.first():
        races = [
            Race(name="Dragonborn", ability_score_increase="Strength +2, Charisma +1", speed=30, traits="Draconic Ancestry, Breath Weapon, Damage Resistance", languages="Common, Draconic"),
            Race(name="Dwarf", ability_score_increase="Constitution +2", speed=25, traits="Darkvision, Dwarven Resilience, Dwarven Combat Training, Tool Proficiency, Stonecunning, Speed is not reduced by heavy armor", languages="Common, Dwarvish"),
            Race(name="Elf", ability_score_increase="Dexterity +2", speed=30, traits="Darkvision, Fey Ancestry, Trance, Keen Senses", languages="Common, Elven"),
            Race(name="Gnome", ability_score_increase="Intelligence +2", speed=25, traits="Darkvision, Gnome Cunning", languages="Common, Gnomish"),
            Race(name="Half-Elf", ability_score_increase="Charisma +2, plus two other ability scores +1", speed=30, traits="Darkvision, Fey Ancestry, Half-Elf Versatility", languages="Common, Elven, one choice"),
            Race(name="Half-Orc", ability_score_increase="Strength +2, Constitution +1", speed=30, traits="Darkvision, Menacing, Relentless Endurance, Savage Attacks", languages="Common, Orc"),
            Race(name="Halfling", ability_score_increase="Dexterity +2", speed=25, traits="Lucky, Brave, Nimble", languages="Common, Halfling"),
            Race(name="Human", ability_score_increase="All ability scores +1", speed=30, traits="None", languages="Common, Choice"),
            Race(name="Tiefling", ability_score_increase="Charisma +2", speed=30, traits="Darkvision, Hellish Resistance", languages="Common, Infernal")
        ]
        db.session.bulk_save_objects(races)
        db.session.commit()
    
    # Provera da li tabela subrace već ima podatke
    if not Subrace.query.first():
        subraces = [
            # Dwarf subraces
            Subrace(name="Hill Dwarf", ability_score_increase="Wisdom +1", traits="Dwarven Toughness", race_id=2),
            Subrace(name="Mountain Dwarf", ability_score_increase="Strength +2", traits="Dwarven Armor Training", race_id=2),
            # Elf subraces
            Subrace(name="Dark Elf", ability_score_increase="Charisma +1", traits="Superior Darkvision, Sunlight Sensitivity, Drow Magic, Drow Weapon Training", race_id=3),
            Subrace(name="High Elf", ability_score_increase="Intelligence +1", traits="Cantrip, Elf Weapon Training, Extra Language", race_id=3),
            Subrace(name="Wood Elf", ability_score_increase="Wisdom +1", traits="Elf Weapon Training, Fleet of Foot, Mask of the Wild", race_id=3),
            # Gnome subraces
            Subrace(name="Forest Gnome", ability_score_increase="Dexterity +1", traits="Natural Illusionist, Speak with Small Beasts", race_id=4),
            Subrace(name="Rock Gnome", ability_score_increase="Constitution +1", traits="Artificer's Lore, Tinker", race_id=4),
            # Halfling subraces
            Subrace(name="Lightfoot", ability_score_increase="Charisma +1", traits="Naturally Stealthy", race_id=7),
            Subrace(name="Stout", ability_score_increase="Constitution +1", traits="Stout Resilience", race_id=7),
            # Tiefling subrace
            Subrace(name="Bloodline of Asmodeus", ability_score_increase="Intelligence +1", traits="Infernal Legacy", race_id=9)
        ]
        db.session.bulk_save_objects(subraces)
        db.session.commit()

    # Provera da li tabela classes već ima podatke
    if not Class.query.first():
        classes = [
            Class(
                name="Barbarian",
                hit_die=12,
                saving_throws="Strength, Constitution",
                armor_proficiencies="Light armor, Medium armor, Shields",
                weapon_proficiencies="Simple weapons, Martial weapons",
                tool_proficiencies="None",
                skill_choices="Animal Handling, Athletics, Intimidation, Nature, Perception, Survival",
                num_skills=2,
                spellcasting=False,
                starting_equipment="- (a) a greataxe or (b) any martial melee weapon\n- (a) two handaxes or (b) any simple weapon\n- An explorer's pack and four javelins",
                class_features="Rage, Unarmored Defense, Danger Sense, Reckless Attack, Primal Path, Ability Score Improvement, Extra Attack, Fast Movement, Feral Instinct, Brutal Critical, Relentless Rage, Persistent Rage, Indomitable Might, Primal Champion"
                ),
            Class(
                name="Bard",
                hit_die=8,
                saving_throws="Dexterity, Charisma",
                armor_proficiencies="Light armor",
                weapon_proficiencies="Simple weapons, hand crossbows, longswords, rapiers, shortswords",
                tool_proficiencies="Three musical instruments of your choice",
                skill_choices="Choose any three",
                num_skills=3,
                spellcasting=True,
                starting_equipment="- (a) a rapier, (b) a longsword, or (c) any simple weapon\n- (a) a diplomat's pack or (b) an entertainer's pack\n- (a) a lute or (b) any other musical instrument\n- Leather armor and a dagger",
                class_features="Spellcasting, Bardic Inspiration, Jack of All Trades, Song of Rest, Bard College, Expertise, Ability Score Improvement, Font of Inspiration, Countercharm, Magical Secrets, Superior Inspiration"
                ),
            Class(
                name="Cleric",
                hit_die=8,
                saving_throws="Wisdom, Charisma",
                armor_proficiencies="Light armor, Medium armor, Shields",
                weapon_proficiencies="All simple weapons",
                tool_proficiencies="None",
                skill_choices="History, Insight, Medicine, Persuasion, Religion",
                num_skills=2,
                spellcasting=True,
                starting_equipment="- (a) a mace or (b) a warhammer (if proficient)\n- (a) scale mail, (b) leather armor, or (c) chain mail (if proficient)\n- (a) a light crossbow and 20 bolts or (b) any simple weapon\n- (a) a priest's pack or (b) an explorer's pack\n- A shield and a holy symbol",
                class_features=" Spellcasting, Divine Domain, Channel Divinity, Ability Score Improvement, Cantrip Versatility, Destroy Undead, Divine Intervention"
                ),
            Class(
                name="Druid",
                hit_die=8,
                saving_throws="Intelligence, Wisdom",
                armor_proficiencies="Light armor, Medium armor, Shields (druids will not wear armor or use shields made of metal)",
                weapon_proficiencies="Clubs, Daggers, Darts, Javelins, Maces, Quarterstaffs, Scimitars, Sickles, Slings, Spears",
                tool_proficiencies="Herbalism kit",
                skill_choices="Arcana, Animal Handling, Insight, Medicine, Nature, Perception, Religion, Survival",
                num_skills=2,
                spellcasting=True,
                starting_equipment="- (a) a wooden shield or (b) any simple weapon\n- (a) a scimitar or (b) any simple melee weapon\n- Leather armor, an explorer's pack, and a druidic focus",
                class_features="Druidic, Spellcasting, Wild Shape, Druid Circle, Ability Score Improvement, Timeless Body, Beast Spells, Archdruid"
                ),
            Class(
                name="Fighter",
                hit_die=10,
                saving_throws="Strength, Constitution",
                armor_proficiencies="All armor, Shields",
                weapon_proficiencies="Simple weapons, Martial weapons",
                tool_proficiencies="None",
                skill_choices="Acrobatics, Animal Handling, Athletics, History, Insight, Intimidation, Perception, Survival",
                num_skills=2,
                spellcasting=False,
                starting_equipment="- (a) chain mail or (b) leather, longbow, and 20 arrows\n- (a) a martial weapon and a shield or (b) two martial weapons\n- (a) a light crossbow and 20 bolts or (b) two handaxes\n- (a) a dungeoneer's pack or (b) an explorer's pack",
                class_features="Fighting Style, Second Wind, Action Surge, Martial Archetype, Ability Score Improvement, Extra Attack, Indomitable"
                ),
            Class(
                name="Monk",
                hit_die=8,
                saving_throws="Strength, Dexterity",
                armor_proficiencies="None",
                weapon_proficiencies="Simple weapons, Shortswords",
                tool_proficiencies="Choose one type of artisan's tools or one musical instrument",
                skill_choices="Acrobatics, Athletics, History, Insight, Religion, Stealth",
                num_skills=2,
                spellcasting=False,
                starting_equipment="- (a) a shortsword or (b) any simple weapon\n- (a) a dungeoneer's pack or (b) an explorer's pack\n- 10 darts",
                class_features="Unarmored Defense, Martial Arts, Ki, Unarmored Movement, Monastic Tradition, Deflect Missiles, Ability Score Improvement, Slow Fall, Extra Attack, Stunning Strike, Ki-Empowered Strikes, Evasion, Stillness of Mind, Purity of Body, Tongue of the Sun and Moon, Diamond Soul, Timeless Body, Empty Body, Perfect Self"
                ),
            Class(
                name="Paladin",
                hit_die=10,
                saving_throws="Wisdom, Charisma",
                armor_proficiencies="All armor, Shields",
                weapon_proficiencies="Simple weapons, Martial weapons",
                tool_proficiencies="None",
                skill_choices="Athletics, Insight, Intimidation, Medicine, Persuasion, Religion",
                num_skills=2,
                spellcasting=True,
                starting_equipment="- (a) a martial weapon and a shield or (b) two martial weapons\n- (a) five javelins or (b) any simple melee weapon\n- (a) a priest's pack or (b) an explorer's pack\n- Chain mail and a holy symbol",
                class_features="Divine Sense, Lay on Hands, Fighting Style, Spellcasting, Divine Smite, Divine Health, Sacred Oath, Ability Score Improvement, Extra Attack, Aura of Protection, Aura of Courage, Improved Divine Smite, Cleansing Touch"
                ),
            Class(
                name="Ranger",
                hit_die=10,
                saving_throws="Strength, Dexterity",
                armor_proficiencies="Light armor, Medium armor, Shields",
                weapon_proficiencies="Simple weapons, Martial weapons",
                tool_proficiencies="None",
                skill_choices="Animal Handling, Athletics, Insight, Investigation, Nature, Perception, Stealth, Survival",
                num_skills=3,
                spellcasting=True,
                starting_equipment="- (a) scale mail or (b) leather armor\n- (a) two shortswords or (b) two simple melee weapons\n- (a) a dungeoneer's pack or (b) an explorer's pack\n- A longbow and a quiver of 20 arrows",
                class_features="Favored Enemy, Natural Explorer, Fighting Style, Spellcasting, Ranger Archetype, Primeval Awareness, Ability Score Improvement, Extra Attack, Land's Stride, Hide in Plain Sight, Vanish, Feral Senses, Foe Slayer"
                ),
            Class(
                name="Rogue",
                hit_die=8,
                saving_throws="Dexterity, Intelligence",
                armor_proficiencies="Light armor",
                weapon_proficiencies="Simple weapons, Hand crossbows, Longswords, Rapiers, Shortswords",
                tool_proficiencies="Thieves' tools",
                skill_choices="Acrobatics, Athletics, Deception, Insight, Intimidation, Investigation, Perception, Performance, Persuasion, Sleight of Hand, Stealth",
                num_skills=4,
                spellcasting=False,
                starting_equipment="- (a) a rapier or (b) a shortsword\n- (a) a shortbow and quiver of 20 arrows or (b) a shortsword\n- (a) a burglar's pack, (b) dungeoneer's pack, or (c) an explorer's pack\n- Leather armor, two daggers, and thieves' tools",
                class_features="Expertise, Sneak Attack, Thieves' Cant, Cunning Action, Roguish Archetype, Ability Score Improvement, Uncanny Dodge, Evasion, Reliable Talent, Blindsense, Slippery Mind, Elusive, Stroke of Luck"
                ),
            Class(
                name="Sorcerer",
                hit_die=6,
                saving_throws="Constitution, Charisma",
                armor_proficiencies="None",
                weapon_proficiencies="Daggers, Darts, Slings, Quarterstaffs, Light crossbows",
                tool_proficiencies="None",
                skill_choices="Arcana, Deception, Insight, Intimidation, Persuasion, Religion",
                num_skills=2,
                spellcasting=True,
                starting_equipment="- (a) a light crossbow and 20 bolts or (b) any simple weapon\n- (a) a component pouch or (b) an arcane focus\n- (a) a dungeoneer's pack or (b) an explorer's pack\n- Two daggers",
                class_features="Spellcasting, Sorcerous Origin, Font of Magic, Metamagic, Ability Score Improvement, Sorcerous Restoration"
                ),
            Class(
                name="Warlock",
                hit_die=8,
                saving_throws="Wisdom, Charisma",
                armor_proficiencies="Light armor",
                weapon_proficiencies="Simple weapons",
                tool_proficiencies="None",
                skill_choices="Arcana, Deception, History, Intimidation, Investigation, Nature, Religion",
                num_skills=2,
                spellcasting=True,
                starting_equipment="- (a) a light crossbow and 20 bolts or (b) any simple weapon\n- (a) a component pouch or (b) an arcane focus\n- (a) a scholar's pack or (b) a dungeoneer's pack\n- Leather armor, any simple weapon, and two daggers",
                class_features="Spellcasting, Otherworldly Patron, Pact Magic, Eldritch Invocations, Pact Boon, Ability Score Improvement, Mystic Arcanum, Eldritch Master"
                ),
            Class(
                name="Wizard",
                hit_die=6,
                saving_throws="Intelligence, Wisdom",
                armor_proficiencies="None",
                weapon_proficiencies="Daggers, darts, slings, quarterstaffs, light crossbows",
                tool_proficiencies="None",
                skill_choices="Arcana, History, Insight, Investigation, Medicine, Religion",
                num_skills=2,
                spellcasting=True,
                starting_equipment="- (a) a quarterstaff or (b) a dagger\n- (a) a component pouch or (b) an arcane focus\n- (a) a scholar's pack or (b) an explorer's pack\n- A spellbook",
                class_features="Spellcasting, Arcane Recovery, Arcane Tradition, Ability Score Improvement, Spell Mastery, Signature Spells"
                ),
        ]
        db.session.bulk_save_objects(classes)
        db.session.commit()

    # Provera da li tabela backgrounds već ima podatke
    if not Background.query.first():
        backgrounds = [
            Background(
                name="Acolyte",
                skill_proficiencies="Insight, Religion",
                tool_proficiencies=None,
                starting_equipment="Holy symbol, prayer book, 5 sticks of incense, vestments, common clothes, pouch with 15 gp",
                starting_gold=15,
                features="Shelter of the Faithful",
                languages="Two of your choice"
            ),
            Background(
                name="Charlatan",
                skill_proficiencies="Deception, Sleight of Hand",
                tool_proficiencies="Disguise kit, Forgery kit",
                starting_equipment="Fine clothes, disguise kit, con tools (bottles, weighted dice, marked cards, or fake signet ring), pouch with 15 gp",
                starting_gold=15,
                features="False Identity",
                languages=None
            ),
            Background(
                name="Criminal",
                skill_proficiencies="Deception, Stealth",
                tool_proficiencies="One type of gaming set, Thieves' tools",
                starting_equipment="Crowbar, dark common clothes with hood, pouch with 15 gp",
                starting_gold=15,
                features="Criminal Contact",
                languages=None
            ),
            Background(
                name="Entertainer",
                skill_proficiencies="Acrobatics, Performance",
                tool_proficiencies="Disguise kit, One type of musical instrument",
                starting_equipment="Musical instrument, favor of admirer, costume, pouch with 15 gp",
                starting_gold=15,
                features="By Popular Demand",
                languages=None
            ),
            Background(
                name="Folk Hero",
                skill_proficiencies="Animal Handling, Survival",
                tool_proficiencies="One type of artisan's tools, Land vehicles",
                starting_equipment="Set of artisan's tools, shovel, iron pot, common clothes, pouch with 10 gp",
                starting_gold=10,
                features="Rustic Hospitality",
                languages=None
            ),
            Background(
                name="Guild Artisan",
                skill_proficiencies="Insight, Persuasion",
                tool_proficiencies="One type of artisan's tools",
                starting_equipment="Set of artisan's tools, letter of introduction, traveler's clothes, pouch with 15 gp",
                starting_gold=15,
                features="Guild Membership",
                languages="One of your choice"
            ),
            Background(
                name="Hermit",
                skill_proficiencies="Medicine, Religion",
                tool_proficiencies="Herbalism kit",
                starting_equipment="Scroll case with notes, winter blanket, common clothes, herbalism kit, pouch with 5 gp",
                starting_gold=5,
                features="Discovery",
                languages="One of your choice"
            ),
            Background(
                name="Noble",
                skill_proficiencies="History, Persuasion",
                tool_proficiencies="One type of gaming set",
                starting_equipment="Fine clothes, signet ring, scroll of pedigree, purse with 25 gp",
                starting_gold=25,
                features="Position of Privilege",
                languages="One of your choice"
            ),
            Background(
                name="Outlander",
                skill_proficiencies="Athletics, Survival",
                tool_proficiencies="One type of musical instrument",
                starting_equipment="Staff, hunting trap, animal trophy, traveler's clothes, pouch with 10 gp",
                starting_gold=10,
                features="Wanderer",
                languages="One of your choice"
            ),
            Background(
                name="Sage",
                skill_proficiencies="Arcana, History",
                tool_proficiencies=None,
                starting_equipment="Ink bottle, quill, small knife, letter from dead colleague, common clothes, pouch with 10 gp",
                starting_gold=10,
                features="Researcher",
                languages="Two of your choice"
            ),
            Background(
                name="Sailor",
                skill_proficiencies="Athletics, Perception",
                tool_proficiencies="Navigator's tools, Vehicles (water)",
                starting_equipment="Belaying pin (club), 50ft silk rope, lucky charm, common clothes, pouch with 10 gp",
                starting_gold=10,
                features="Ship's Passage",
                languages=None
            ),
            Background(
                name="Soldier",
                skill_proficiencies="Athletics, Intimidation",
                tool_proficiencies="One type of gaming set, Land vehicles",
                starting_equipment="Insignia of rank, trophy from fallen enemy, dice or deck of cards, common clothes, pouch with 10 gp",
                starting_gold=10,
                features="Military Rank",
                languages=None
            ),
            Background(
                name="Urchin",
                skill_proficiencies="Sleight of Hand, Stealth",
                tool_proficiencies="Disguise kit, Thieves' tools",
                starting_equipment="Small knife, city map, pet mouse, token of parents, common clothes, pouch with 10 gp",
                starting_gold=10,
                features="City Secrets",
                languages=None
            ),
        ]
        db.session.bulk_save_objects(backgrounds)
        db.session.commit()

# Funkcija za dobijanje svih entiteta sa samo ID-jem i imenom
def get_all_entities(model):
    # Dohvati sve zapise iz modela
    records = model.query.all()
    
    # Kreiraj listu sa ID-jem i imenom za svaki zapis
    result = [{'id': r.id, 'name': r.name} for r in records]
    
    # Vrati podatke kao JSON
    return jsonify(result), 200

# Funkcija za dobijanje detalja entiteta (uključujući opis)
def get_entity_details(model, description_model, entity_id):
    # Dohvati entitet sa zadatim ID-em
    entity = model.query.get(entity_id)
    if not entity:
        return jsonify({'error': f'{model.__name__} not found'}), 404

    # Dohvati opis entiteta
    description_entry = description_model.query.filter_by(**{f'{model.__name__.lower()}_id': entity_id}).first()

    # Kreiraj i vrati JSON odgovor
    return jsonify({
        'id': entity.id,
        'name': entity.name,
        'description': description_entry.description if description_entry else "No description available."
    }), 200

# Pomoćna funkcija za vraćanje spellova sa paginacijom i pretragom
def get_paginated_spells(query):
    # Uzimanje query parametara za paginaciju i pretragu
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str).strip()
    spell_type_filter = request.args.get('spell_type', '', type=str).strip()
    spell_level_filter = request.args.get('spell_level', '', type=str).strip()

    # Ako postoji search, dodaj filter po imenu magije
    if search:
        query = query.filter(Spell.spell_name.ilike(f'%{search}%'))

    # Ako postoji filter po tipu magije
    if spell_type_filter:
        query = query.filter(Spell.spell_type.ilike(f'%{spell_type_filter}%'))

    # Ako postoji filter po nivou magije
    if spell_level_filter != '':
        query = query.filter(Spell.spell_level == int(spell_level_filter))

    # Paginacija sa izabranim query-jem
    spells = query.paginate(page=page, per_page=per_page, error_out=False)

    # Formatiranje spellova
    result = [{
        'spell_id': spell.spell_id,
        'spell_name': spell.spell_name,
        'spell_level': spell.spell_level,
        'spell_type': spell.spell_type,
        'casting_time': spell.casting_time,
        'spell_range': spell.spell_range,
        'components': spell.components,
        'duration': spell.duration,
        'description': spell.description,
        'higher_levels': spell.higher_levels
    } for spell in spells.items]

    return jsonify({
        'spells': result,
        'total': spells.total,
        'pages': spells.pages,
        'current_page': spells.page
    }), 200

# Funkcija za proveru dozvoljene ekstenzije
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------- ROUTE DEFINICIJE ---------------- #

# Ruta za registraciju
@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"message": "Username or email already exists"}), 409

    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registration successful"}), 200

# Ruta za čuvanje karaktera
@app.route('/api/characters', methods=['POST'])
@jwt_required()
def create_character():
    data = request.get_json()
    user_id = get_jwt_identity()

    char = Character(
        name=data['name'],
        race=data['race'],
        char_class=data['class'],
        level=data.get('level', 1),
        user_id=user_id
    )

    db.session.add(char)
    db.session.commit()
    return jsonify({"message": "Character created"}), 201

# Ruta za prijavu (login)
@app.route('/api/login', methods=['POST'])
def login():
    # Provera da li su podaci u JSON formatu
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400

    data = request.get_json()
    
    # Obavezna provera polja
    if not data.get('username') or not data.get('password'):
        return jsonify({"message": "Missing username or password"}), 400

    username = data['username']
    password = data['password']

    try:
        # Pronalaženje korisnika
        user = User.query.filter_by(username=username).first()

        if not user:
            # Bezbednosna napomena: Ne otkrivamo da korisnik ne postoji
            return jsonify({"message": "Invalid credentials"}), 401

        # Provera lozinke
        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({"message": "Invalid credentials"}), 401

        # Kreiranje JWT tokena
        access_token = create_access_token(
            identity=str(user.id),  # Convert user.id to string
            additional_claims={"username": user.username}  # Dodatni podaci u tokenu
        )

        # Kreiranje odgovora sa tokenom
        return jsonify({
            "message": "Login successful",
            "username": user.username,
            "user_id": user.id,
            "access_token": access_token
        }), 200

    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500
    
# Ruta za proveru sesije
@app.route('/api/check_session', methods=['GET'])
@jwt_required()
def check_session():
    try:
        user_id = get_jwt_identity()
        print(f"DEBUG: Token je validan. User ID: {user_id}")
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "Unauthorized"}), 401
        return jsonify({"loggedIn": True, "username": user.username, "user_id": user.id}), 200
    except Exception as e:
        print(f"DEBUG: Greška pri proveri sesije: {str(e)}")
        return jsonify({"message": "Unauthorized"}), 401

# Ruta za odjavljivanje (logout)
@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    # Ovaj logout samo znači da je korisnik odjavljen na frontend strani
    return jsonify({"message": "Logout successful"}), 200

# Ruta za dobijanje svih rasa (samo imena i ID-jevi)
@app.route('/api/races', methods=['GET'])
def get_races():
    return get_all_entities(Race)  # Koristi generičku funkciju za rase

# Ruta za dobijanje opisa rase po ID-ju
@app.route('/api/races/<int:race_id>', methods=['GET'])
def get_race_details(race_id):
    return get_entity_details(Race, RaceDescription, race_id)

# Ruta za dobijanje rase po imenu
@app.route('/api/races/name/<race_name>', methods=['GET'])
def get_race_by_name(race_name):
    race = Race.query.filter_by(name=race_name).first_or_404()
    return jsonify({
        'id': race.id,
        'name': race.name,
        'ability_score_increase': race.ability_score_increase,
        'speed': race.speed,
        'traits': race.traits,
        'languages': race.languages,
        'proficiency': race.proficiency
    })

# Ruta za dobijanje svih podrasa (samo imena i ID-jevi)
@app.route('/api/races/<int:race_id>/subraces', methods=['GET'])
def get_subraces(race_id):
    subraces = Subrace.query.filter_by(race_id=race_id).all()
    return jsonify([{
        'id': subrace.id,
        'name': subrace.name,
        'ability_score_increase': subrace.ability_score_increase,
        'traits': subrace.traits,
        'proficiency': subrace.proficiency
    } for subrace in subraces])

# Ruta za dobijanje svih klasa (samo imena i ID-jevi)
@app.route('/api/classes', methods=['GET'])
def get_classes():
    return get_all_entities(Class)  # Koristi generičku funkciju za klase

# Ruta za dobijanje opisa klase po ID-ju
@app.route('/api/classes/<int:class_id>', methods=['GET'])
def get_class_details(class_id):
    return get_entity_details(Class, ClassDescription, class_id)

# Ruta za dobijanje detalja klase po imenu
@app.route('/api/classes/name/<class_name>', methods=['GET'])
def get_class_by_name(class_name):
    class_data = Class.query.filter_by(name=class_name).first()
    if class_data:
        return jsonify({
            'id': class_data.id,
            'name': class_data.name,
            'hit_die': class_data.hit_die,
            'saving_throws': class_data.saving_throws,
            'armor_proficiencies': class_data.armor_proficiencies,
            'weapon_proficiencies': class_data.weapon_proficiencies,
            'tool_proficiencies': class_data.tool_proficiencies,
            'skill_choices': class_data.skill_choices,
            'num_skills': class_data.num_skills,
            'spellcasting': class_data.spellcasting,
            'starting_equipment': class_data.starting_equipment,
            'class_features': class_data.class_features,
            'spellcasting_ability': class_data.spellcasting_ability
        })
    return jsonify({'error': 'Class not found'}), 404

# Ruta za dobijanje magija (spells) sa podrškom za paginaciju
@app.route('/api/spells', methods=['GET'])
def get_spells():
    # Prosledi osnovni Spell query bez filtera i poređaj po abecednom redu
    return get_paginated_spells(Spell.query.order_by(Spell.spell_name.asc()))

# Ruta za dobijanje opisa magija (spell) po ID-ju
@app.route('/api/spells/<int:spell_id>', methods=['GET'])
def get_spell_details(spell_id):
    spell = Spell.query.get(spell_id)
    if not spell:
        return jsonify({'error': 'Spell not found'}), 404

    return jsonify({
        'spell_id': spell.spell_id,
        'spell_name': spell.spell_name,
        'spell_level': spell.spell_level,
        'spell_type': spell.spell_type,
        'casting_time': spell.casting_time,
        'spell_range': spell.spell_range,
        'components': spell.components,
        'duration': spell.duration,
        'description': spell.description,
        'higher_levels': spell.higher_levels
    }), 200

# Ruta za dobijanje magija (spell) na osnovu klase
@app.route('/api/spells/by-class/<int:class_id>', methods=['GET'])
def get_spells_by_class(class_id):
    # Napravi upit koji spaja Spell i ClassSpell
    query = db.session.query(Spell).join(ClassSpell).filter(ClassSpell.class_id == class_id)
    return get_paginated_spells(query)

# Ruta za dobijanje svih pozadina (samo imena i ID-jevi)
@app.route('/api/backgrounds', methods=['GET'])
def get_backgrounds():
    return get_all_entities(Background)  # Koristi generičku funkciju za pozadine

# Ruta za dobijanje opisa pozadine po ID-ju
@app.route('/api/backgrounds/<int:background_id>', methods=['GET'])
def get_background_details(background_id):
    return get_entity_details(Background, BackgroundDescription, background_id)

# Ruta za dobijanje pozadine po imenu
@app.route('/api/backgrounds/name/<background_name>', methods=['GET'])
def get_background_by_name(background_name):
    background = Background.query.filter_by(name=background_name).first()
    if background:
        return jsonify({
            'id': background.id,
            'name': background.name,
            'skill_proficiencies': background.skill_proficiencies,
            'tool_proficiencies': background.tool_proficiencies,
            'starting_equipment': background.starting_equipment,
            'starting_gold': background.starting_gold,
            'features': background.features,
            'languages': background.languages,
            'personality_trait': background.personality_trait,
            'ideal': background.ideal,
            'bond': background.bond,
            'flaw': background.flaw,
            'variant': background.variant
        })
    return jsonify({'error': 'Background not found'}), 404

# Ruta za dobijanje magija (spells) određenog nivoa bez paginacije - samo osnovna lista
@app.route('/api/spells/by-level/<int:level>', methods=['GET'])
def get_spells_by_level_simple(level):
    # Pronađi sve spellove određenog nivoa
    query = Spell.query.filter_by(spell_level=level)
    
    # Filtriraj prema tipu (školi) magije ako je prosleđen
    spell_type_filter = request.args.get('spell_type', '', type=str).strip()
    if spell_type_filter:
        query = query.filter(Spell.spell_type.ilike(f'%{spell_type_filter}%'))
    
    # Filtriraj prema klasi ako je prosleđena
    class_id = request.args.get('class_id', type=int)
    if class_id:
        query = query.join(ClassSpell).filter(ClassSpell.class_id == class_id)
    
    # Sortiraj po abecednom redu i dohvati sve
    spells = query.order_by(Spell.spell_name.asc()).all()
    
    # Vrati osnovne podatke i dodatne atribute potrebne za filtere
    result = [{
        'spell_id': spell.spell_id,
        'spell_name': spell.spell_name,
        'spell_type': spell.spell_type  # Dodajemo tip za filtriranje na frontendu
    } for spell in spells]
    
    return jsonify({
        'spells': result,
        'count': len(result)
    }), 200

# Dodajem novu rutu za dobijanje svih magija određene klase bez paginacije
@app.route('/api/spells/by-class/<int:class_id>/all', methods=['GET'])
def get_spells_by_class_all(class_id):
    # Napravi upit koji spaja Spell i ClassSpell
    query = db.session.query(Spell).join(ClassSpell).filter(ClassSpell.class_id == class_id)
    
    # Filtriraj prema nivou magije ako je prosleđen
    spell_level_filter = request.args.get('spell_level', '', type=str).strip()
    if spell_level_filter != '':
        query = query.filter(Spell.spell_level == int(spell_level_filter))
        
    # Filtriraj prema tipu (školi) magije ako je prosleđen
    spell_type_filter = request.args.get('spell_type', '', type=str).strip()
    if spell_type_filter:
        query = query.filter(Spell.spell_type.ilike(f'%{spell_type_filter}%'))
    
    # Sortiraj po abecednom redu i dohvati sve
    spells = query.order_by(Spell.spell_name.asc()).all()
    
    # Pripremi podatke za odgovor
    result = [{
        'spell_id': spell.spell_id,
        'spell_name': spell.spell_name,
        'spell_level': spell.spell_level,
        'spell_type': spell.spell_type,
        'casting_time': spell.casting_time,
        'spell_range': spell.spell_range,
        'components': spell.components,
        'duration': spell.duration,
        'description': spell.description,
        'higher_levels': spell.higher_levels
    } for spell in spells]
    
    return jsonify({
        'spells': result,
        'count': len(result)
    }), 200

# Ruta za kontrolnu tablu
@app.route('/api/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Dohvati sve karaktere korisnika
        characters = Character.query.filter_by(user_id=user_id).all()
        
        # Pripremi samo osnovne informacije o karakterima
        character_list = [{
            'id': char.id,
            'name': char.name
        } for char in characters]
        
        return jsonify({
            "username": user.username,
            "characters": character_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch dashboard data',
            'details': str(e)
        }), 500

# Ruta za brisanje jednog korisnika
@app.route('/api/users/<int:id>', methods=['DELETE', 'OPTIONS'])
@jwt_required(optional=True)
def delete_user(id):
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'DELETE')
        return response
        
    user_id = get_jwt_identity()  # Uzmi ID korisnika iz JWT-a
    user = User.query.get(id)

    if user and str(user.id) == str(user_id):  # Proveri da li je korisnik isti kao onaj koji pokušava da obriše
        try:
            # Prvo obriši sve karaktere korisnika
            characters = Character.query.filter_by(user_id=user.id).all()
            for character in characters:
                db.session.delete(character)

            # Zatim obriši korisnika
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'User deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Greška pri brisanju korisnika: {str(e)}")
            return jsonify({'message': 'Error deleting user', 'error': str(e)}), 500
    else:
        return jsonify({'message': 'User not found or unauthorized'}), 404

# Ruta za čuvanje karaktera
@app.route('/api/characters', methods=['POST'])
@jwt_required()
def create_character():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Kreiranje novog karaktera
        new_character = Character(
            name=data['name'],
            player_name=data['playerName'],
            char_class=data['class'],
            level=data['level'],
            background=data['background'],
            background_variant=data.get('backgroundVariant'),
            race=data['race'],
            subrace=data.get('subrace'),
            alignment=data.get('alignment'),
            experience_points=data.get('experiencePoints'),
            hit_die=data.get('hitDie'),
            hit_dice=data.get('hitDice', 1),
            
            # Choices podaci
            selectable_skills=data.get('selectableSkills', []),
            max_selectable_skills=data.get('maxSelectableSkills', 0),
            previous_race_bonus=data.get('previousRaceBonus', 0),
            previous_class_choices=data.get('previousClassChoices', 0),
            previous_overlap_count=data.get('previousOverlapCount', 0),
            
            # Ability scores
            strength_score=data['abilities']['Strength']['score'],
            dexterity_score=data['abilities']['Dexterity']['score'],
            constitution_score=data['abilities']['Constitution']['score'],
            intelligence_score=data['abilities']['Intelligence']['score'],
            wisdom_score=data['abilities']['Wisdom']['score'],
            charisma_score=data['abilities']['Charisma']['score'],
            
            # JSON fields
            saving_throws=data['savingThrows'],
            skills=data['skills'],
            death_saves=data['deathSaves'],
            attacks=data.get('attacks', []),  # Dodajemo polje za napade
            spell_slots=data.get('spellSlots', {}),  # Dodajemo spell slots
            
            # HP and combat
            hp_max=data['hp']['max'],
            hp_current=data['hp']['current'],
            hp_temp=data['hp']['temp'],
            hp_base=data['hp']['base'],
            ac=data['ac'],
            initiative=data['initiative'],
            speed=data['speed'],
            
            # Passive Wisdom
            passive_wisdom=data.get('passiveWisdom', 10),
            passive_wisdom_base=data.get('passiveWisdomBase', 10),
            passive_wisdom_manual_modifier=data.get('passiveWisdomManualModifier', 0),
            
            # Currency
            currency_cp=data.get('currency', {}).get('cp', 0) or 0,
            currency_sp=data.get('currency', {}).get('sp', 0) or 0,
            currency_ep=data.get('currency', {}).get('ep', 0) or 0,
            currency_gp=data.get('currency', {}).get('gp', 0) or 0,
            currency_pp=data.get('currency', {}).get('pp', 0) or 0,
            
            # Equipment and features
            equipment=data.get('equipment'),
            race_features=data.get('raceFeatures'),
            class_features=data.get('classFeatures'),
            race_proficiency=data.get('raceProficiency'),
            class_proficiency=data.get('classProficiency'),
            background_features=data.get('backgroundFeatures'),
            armor=data.get('armor'),
            has_shield=data.get('hasShield', False),
            
            # Personality
            personality_traits=data.get('personality', {}).get('traits'),
            personality_ideals=data.get('personality', {}).get('ideals'),
            personality_bonds=data.get('personality', {}).get('bonds'),
            personality_flaws=data.get('personality', {}).get('flaws'),
            
            # Proficiency and Inspiration
            proficiency_bonus=data.get('proficiencyBonus', 2),
            prof_bonus_modifier=data.get('profBonusModifier', 0),
            inspiration_value=data.get('inspirationValue', 0),
            
            # Physical characteristics
            age=data.get('age'),
            height=data.get('height'),
            weight=data.get('weight'),
            eyes=data.get('eyes'),
            skin=data.get('skin'),
            hair=data.get('hair'),
            
            # Backstory and appearance
            backstory=data.get('backstory'),
            allies=data.get('allies'),
            treasure=data.get('treasure'),
            
            # Images
            appearance_image_path=data.get('appearanceImage'),
            symbol_image_path=data.get('symbolImage'),
            symbol_name=data.get('symbolName'),
            
            # Spellcasting
            spellcasting_ability=data.get('spellcasting', {}).get('ability'),
            spellcasting_save_dc=data.get('spellcasting', {}).get('saveDC', 8),
            spellcasting_attack_bonus=data.get('spellcasting', {}).get('attackBonus', 0),
            
            # Base vrednosti za bojenje
            base_ability_scores=data.get('baseAbilityScores'),
            base_race_scores=data.get('baseRaceScores'),
            pure_race_scores=data.get('pureRaceScores'),
            base_speed=data.get('baseSpeed', 30),
            
            # Manualni modifikatori
            ac_manual_modifier=data.get('acManualModifier', 0),
            spell_save_dc_manual_modifier=data.get('spellSaveDCManualModifier', 0),
            spell_attack_bonus_manual_modifier=data.get('spellAttackBonusManualModifier', 0),
            initiative_modifier=data.get('initiativeModifier', 0),
            saving_throw_manual_modifiers=data.get('savingThrowManualModifiers'),
            skill_manual_modifiers=data.get('skillManualModifiers'),
            
            # Spells - prilagođavamo za frontend strukturu spells.levelX
            cantrips=data.get('spells', {}).get('cantrips', []),
            level1_spells=data.get('spells', {}).get('level1', []),
            level2_spells=data.get('spells', {}).get('level2', []),
            level3_spells=data.get('spells', {}).get('level3', []),
            level4_spells=data.get('spells', {}).get('level4', []),
            level5_spells=data.get('spells', {}).get('level5', []),
            level6_spells=data.get('spells', {}).get('level6', []),
            level7_spells=data.get('spells', {}).get('level7', []),
            level8_spells=data.get('spells', {}).get('level8', []),
            level9_spells=data.get('spells', {}).get('level9', []),
            
            user_id=user_id
        )
        
        db.session.add(new_character)
        db.session.commit()
        
        return jsonify({
            'message': 'Character created successfully',
            'character_id': new_character.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create character',
            'details': str(e)
        }), 500

# Ruta za dobijanje svih karaktera trenutnog korisnika
@app.route('/api/characters', methods=['GET'])
@jwt_required()
def get_characters():
    try:
        user_id = get_jwt_identity()
        characters = Character.query.filter_by(user_id=user_id).all()
        
        return jsonify([{
            'id': char.id,
            'name': char.name,
            'player_name': char.player_name,
            'char_class': char.char_class,
            'level': char.level,
            'race': char.race,
            'subrace': char.subrace,
            'background': char.background,
            'created_at': char.created_at.isoformat() if char.created_at else None,
            'updated_at': char.updated_at.isoformat() if char.updated_at else None
        } for char in characters]), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch characters',
            'details': str(e)
        }), 500

# Ruta za dobijanje jednog karaktera po ID-ju
@app.route('/api/characters/<int:character_id>', methods=['GET'])
@jwt_required()
def get_character(character_id):
    try:
        user_id = get_jwt_identity()
        character = Character.query.filter_by(id=character_id, user_id=user_id).first()
        
        if not character:
            return jsonify({'error': 'Character not found'}), 404
            
        return jsonify({
            'id': character.id,
            'name': character.name,
            'playerName': character.player_name,
            'class': character.char_class,
            'level': character.level,
            'background': character.background,
            'backgroundVariant': character.background_variant,
            'race': character.race,
            'subrace': character.subrace,
            'alignment': character.alignment,
            'experiencePoints': character.experience_points,
            'hitDie': character.hit_die,
            'hitDice': character.hit_dice,
            
            # Choices podaci
            'selectableSkills': character.selectable_skills,
            'maxSelectableSkills': character.max_selectable_skills,
            'previousRaceBonus': character.previous_race_bonus,
            'previousClassChoices': character.previous_class_choices,
            'previousOverlapCount': character.previous_overlap_count,
            
            # Ability scores
            'abilities': {
                'Strength': {'score': character.strength_score},
                'Dexterity': {'score': character.dexterity_score},
                'Constitution': {'score': character.constitution_score},
                'Intelligence': {'score': character.intelligence_score},
                'Wisdom': {'score': character.wisdom_score},
                'Charisma': {'score': character.charisma_score}
            },
            
            # JSON fields
            'savingThrows': character.saving_throws,
            'skills': character.skills,
            'deathSaves': character.death_saves,
            'attacks': character.attacks,  # Dodato polje za napade
            'spellSlots': character.spell_slots,  # Dodato polje za spell slots
            
            # HP and combat
            'hp': {
                'max': character.hp_max,
                'current': character.hp_current,
                'temp': character.hp_temp,
                'base': character.hp_base
            },
            'ac': character.ac,
            'initiative': character.initiative,
            'speed': character.speed,
            
            # Passive Wisdom
            'passiveWisdom': character.passive_wisdom,
            'passiveWisdomBase': character.passive_wisdom_base,
            'passiveWisdomManualModifier': character.passive_wisdom_manual_modifier,
            
            # Currency
            'currency': {
                'cp': character.currency_cp,
                'sp': character.currency_sp,
                'ep': character.currency_ep,
                'gp': character.currency_gp,
                'pp': character.currency_pp
            },
            
            # Equipment and features
            'equipment': character.equipment,
            'raceFeatures': character.race_features,
            'classFeatures': character.class_features,
            'raceProficiency': character.race_proficiency,
            'classProficiency': character.class_proficiency,
            'backgroundFeatures': character.background_features,
            'armor': character.armor,
            'hasShield': character.has_shield,
            
            # Personality
            'personality': {
                'traits': character.personality_traits,
                'ideals': character.personality_ideals,
                'bonds': character.personality_bonds,
                'flaws': character.personality_flaws
            },
            
            # Proficiency and Inspiration
            'proficiencyBonus': character.proficiency_bonus,
            'profBonusModifier': character.prof_bonus_modifier,
            'inspirationValue': character.inspiration_value,
            
            # Physical characteristics
            'age': character.age,
            'height': character.height,
            'weight': character.weight,
            'eyes': character.eyes,
            'skin': character.skin,
            'hair': character.hair,
            
            # Backstory and appearance
            'backstory': character.backstory,
            'allies': character.allies,
            'treasure': character.treasure,
            
            # Images
            'appearanceImage': character.appearance_image_path,
            'symbolImage': character.symbol_image_path,
            'symbolName': character.symbol_name,
            
            # Spellcasting
            'spellcasting': {
                'ability': character.spellcasting_ability,
                'saveDC': character.spellcasting_save_dc,
                'attackBonus': character.spellcasting_attack_bonus
            },
            
            # Base vrednosti za bojenje
            'baseAbilityScores': character.base_ability_scores,
            'baseRaceScores': character.base_race_scores,
            'pureRaceScores': character.pure_race_scores,
            'baseSpeed': character.base_speed,
            
            # Manualni modifikatori
            'acManualModifier': character.ac_manual_modifier,
            'spellSaveDCManualModifier': character.spell_save_dc_manual_modifier,
            'spellAttackBonusManualModifier': character.spell_attack_bonus_manual_modifier,
            'initiativeModifier': character.initiative_modifier,
            'savingThrowManualModifiers': character.saving_throw_manual_modifiers,
            'skillManualModifiers': character.skill_manual_modifiers,
            
            # Spells - prilagođavamo format za frontend
            'spells': {
                'cantrips': character.cantrips or [],
                'level1': character.level1_spells or [],
                'level2': character.level2_spells or [],
                'level3': character.level3_spells or [],
                'level4': character.level4_spells or [],
                'level5': character.level5_spells or [],
                'level6': character.level6_spells or [],
                'level7': character.level7_spells or [],
                'level8': character.level8_spells or [],
                'level9': character.level9_spells or []
            },
            
            'created_at': character.created_at.isoformat() if character.created_at else None,
            'updated_at': character.updated_at.isoformat() if character.updated_at else None
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch character',
            'details': str(e)
        }), 500

# Ruta za ažuriranje karaktera
@app.route('/api/characters/<int:character_id>', methods=['PUT'])
@jwt_required()
def update_character(character_id):
    try:
        user_id = get_jwt_identity()
        character = Character.query.filter_by(id=character_id, user_id=user_id).first()
        
        if not character:
            return jsonify({'error': 'Character not found'}), 404
            
        data = request.get_json()
        
        # Ažuriranje svih polja
        character.name = data.get('name', character.name)
        character.player_name = data.get('playerName', character.player_name)
        character.char_class = data.get('class', character.char_class)
        character.level = data.get('level', character.level)
        character.background = data.get('background', character.background)
        character.background_variant = data.get('backgroundVariant', character.background_variant)
        character.race = data.get('race', character.race)
        character.subrace = data.get('subrace', character.subrace)
        character.alignment = data.get('alignment', character.alignment)
        character.experience_points = data.get('experiencePoints', character.experience_points)
        character.hit_die = data.get('hitDie', character.hit_die)
        character.hit_dice = data.get('hitDice', character.hit_dice)
        
        # Choices podaci
        character.selectable_skills = data.get('selectableSkills', character.selectable_skills)
        character.max_selectable_skills = data.get('maxSelectableSkills', character.max_selectable_skills)
        character.previous_race_bonus = data.get('previousRaceBonus', character.previous_race_bonus)
        character.previous_class_choices = data.get('previousClassChoices', character.previous_class_choices)
        character.previous_overlap_count = data.get('previousOverlapCount', character.previous_overlap_count)
        
        # Ability scores
        if 'abilities' in data:
            character.strength_score = data['abilities']['Strength']['score']
            character.dexterity_score = data['abilities']['Dexterity']['score']
            character.constitution_score = data['abilities']['Constitution']['score']
            character.intelligence_score = data['abilities']['Intelligence']['score']
            character.wisdom_score = data['abilities']['Wisdom']['score']
            character.charisma_score = data['abilities']['Charisma']['score']
        
        # JSON fields
        if 'savingThrows' in data:
            character.saving_throws = data['savingThrows']
        if 'skills' in data:
            character.skills = data['skills']
        if 'deathSaves' in data:
            character.death_saves = data['deathSaves']
        if 'attacks' in data:
            character.attacks = data['attacks']
        if 'spellSlots' in data:
            character.spell_slots = data['spellSlots']
        
        # HP and combat
        if 'hp' in data:
            character.hp_max = data['hp']['max']
            character.hp_current = data['hp']['current']
            character.hp_temp = data['hp']['temp']
            character.hp_base = data['hp']['base']
        character.ac = data.get('ac', character.ac)
        character.initiative = data.get('initiative', character.initiative)
        character.speed = data.get('speed', character.speed)
        
        # Passive Wisdom
        character.passive_wisdom = data.get('passiveWisdom', character.passive_wisdom)
        character.passive_wisdom_base = data.get('passiveWisdomBase', character.passive_wisdom_base)
        character.passive_wisdom_manual_modifier = data.get('passiveWisdomManualModifier', character.passive_wisdom_manual_modifier)
        
        # Currency
        if 'currency' in data:
            character.currency_cp = data['currency'].get('cp', 0) or 0
            character.currency_sp = data['currency'].get('sp', 0) or 0
            character.currency_ep = data['currency'].get('ep', 0) or 0
            character.currency_gp = data['currency'].get('gp', 0) or 0
            character.currency_pp = data['currency'].get('pp', 0) or 0
        
        # Equipment and features
        character.equipment = data.get('equipment', character.equipment)
        character.race_features = data.get('raceFeatures', character.race_features)
        character.class_features = data.get('classFeatures', character.class_features)
        character.race_proficiency = data.get('raceProficiency', character.race_proficiency)
        character.class_proficiency = data.get('classProficiency', character.class_proficiency)
        character.background_features = data.get('backgroundFeatures', character.background_features)
        character.armor = data.get('armor', character.armor)
        character.has_shield = data.get('hasShield', character.has_shield)
        
        # Personality
        if 'personality' in data:
            character.personality_traits = data['personality'].get('traits', character.personality_traits)
            character.personality_ideals = data['personality'].get('ideals', character.personality_ideals)
            character.personality_bonds = data['personality'].get('bonds', character.personality_bonds)
            character.personality_flaws = data['personality'].get('flaws', character.personality_flaws)
        
        # Proficiency and Inspiration
        if 'proficiencyBonus' in data:
            character.proficiency_bonus = data['proficiencyBonus']
        if 'profBonusModifier' in data:
            character.prof_bonus_modifier = data['profBonusModifier']
        if 'inspirationValue' in data:
            character.inspiration_value = data['inspirationValue']
        
        # Physical characteristics
        character.age = data.get('age', character.age)
        character.height = data.get('height', character.height)
        character.weight = data.get('weight', character.weight)
        character.eyes = data.get('eyes', character.eyes)
        character.skin = data.get('skin', character.skin)
        character.hair = data.get('hair', character.hair)
        
        # Backstory and appearance
        character.backstory = data.get('backstory', character.backstory)
        character.allies = data.get('allies', character.allies)
        character.treasure = data.get('treasure', character.treasure)
        
        # Images
        character.appearance_image_path = data.get('appearanceImage', character.appearance_image_path)
        character.symbol_image_path = data.get('symbolImage', character.symbol_image_path)
        character.symbol_name = data.get('symbolName', character.symbol_name)
        
        # Spellcasting
        if 'spellcasting' in data:
            character.spellcasting_ability = data['spellcasting'].get('ability', character.spellcasting_ability)
            character.spellcasting_save_dc = data['spellcasting'].get('saveDC', character.spellcasting_save_dc)
            character.spellcasting_attack_bonus = data['spellcasting'].get('attackBonus', character.spellcasting_attack_bonus)
        
        # Base vrednosti za bojenje
        if 'baseAbilityScores' in data:
            character.base_ability_scores = data['baseAbilityScores']
        if 'baseRaceScores' in data:
            character.base_race_scores = data['baseRaceScores']
        if 'pureRaceScores' in data:
            character.pure_race_scores = data['pureRaceScores']
        if 'baseSpeed' in data:
            character.base_speed = data['baseSpeed']
            
        # Manualni modifikatori
        if 'acManualModifier' in data:
            character.ac_manual_modifier = data['acManualModifier']
        if 'spellSaveDCManualModifier' in data:
            character.spell_save_dc_manual_modifier = data['spellSaveDCManualModifier']
        if 'spellAttackBonusManualModifier' in data:
            character.spell_attack_bonus_manual_modifier = data['spellAttackBonusManualModifier']
        if 'initiativeModifier' in data:
            character.initiative_modifier = data['initiativeModifier']
        if 'savingThrowManualModifiers' in data:
            character.saving_throw_manual_modifiers = data['savingThrowManualModifiers']
        if 'skillManualModifiers' in data:
            character.skill_manual_modifiers = data['skillManualModifiers']
        
        # Spells - prilagođavamo za frontend strukturu spells.levelX
        if 'spells' in data:
            character.cantrips = data['spells'].get('cantrips', character.cantrips)
            character.level1_spells = data['spells'].get('level1', character.level1_spells)
            character.level2_spells = data['spells'].get('level2', character.level2_spells)
            character.level3_spells = data['spells'].get('level3', character.level3_spells)
            character.level4_spells = data['spells'].get('level4', character.level4_spells)
            character.level5_spells = data['spells'].get('level5', character.level5_spells)
            character.level6_spells = data['spells'].get('level6', character.level6_spells)
            character.level7_spells = data['spells'].get('level7', character.level7_spells)
            character.level8_spells = data['spells'].get('level8', character.level8_spells)
            character.level9_spells = data['spells'].get('level9', character.level9_spells)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Character updated successfully',
            'character_id': character.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update character',
            'details': str(e)
        }), 500

# Ruta za brisanje karaktera
@app.route('/api/characters/<int:character_id>', methods=['DELETE'])
@jwt_required()
def delete_character(character_id):
    try:
        user_id = get_jwt_identity()
        character = Character.query.filter_by(id=character_id, user_id=user_id).first()
        
        if not character:
            return jsonify({'error': 'Character not found'}), 404
            
        db.session.delete(character)
        db.session.commit()
        
        return jsonify({
            'message': 'Character deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete character',
            'details': str(e)
        }), 500

# Ruta za upload slika
@app.route('/api/upload-image', methods=['POST'])
@jwt_required()
def upload_image():
    try:
        user_id = get_jwt_identity()
        
        # Proveri da li je fajl u zahtevu
        if 'image' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['image']
        
        # Ako korisnik nije izabrao fajl
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Ako je fajl dozvoljen
        if file and allowed_file(file.filename):
            # Kreiraj bezbedno ime fajla
            filename = secure_filename(file.filename)
            # Dodaj jedinstveni id da izbegnemo overwrite
            unique_filename = f"{uuid.uuid4()}_{filename}"
            # Kreiraj direktorijum za korisnika ako ne postoji
            user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
            
            # Sačuvaj fajl
            file_path = os.path.join(user_folder, unique_filename)
            file.save(file_path)
            
            # Vrati relativnu putanju do fajla
            relative_path = f"/uploads/{user_id}/{unique_filename}"
            
            return jsonify({
                'success': True,
                'image_path': relative_path
            }), 200
            
        return jsonify({'error': 'File type not allowed'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta za preuzimanje slika
@app.route('/uploads/<user_id>/<filename>', methods=['GET'])
def uploaded_file(user_id, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], user_id), filename)

# Ruta za ažuriranje korisničkog imena
@app.route('/api/update-username', methods=['PUT'])
@jwt_required()
def update_username():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'username' not in data:
            return jsonify({'message': 'Username is required'}), 400
            
        new_username = data['username'].strip()
        
        if not new_username:
            return jsonify({'message': 'Username cannot be empty'}), 400
            
        # Proveri da li korisničko ime već postoji
        existing_user = User.query.filter(User.username == new_username, User.id != user_id).first()
        if existing_user:
            return jsonify({'message': 'Username already exists'}), 409
            
        # Pronađi i ažuriraj korisnika
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        user.username = new_username
        db.session.commit()
        
        return jsonify({'message': 'Username updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating username: {str(e)}'}), 500

# Ruta za ažuriranje lozinke
@app.route('/api/update-password', methods=['PUT'])
@jwt_required()
def update_password():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'currentPassword' not in data or 'newPassword' not in data:
            return jsonify({'message': 'Current password and new password are required'}), 400
            
        current_password = data['currentPassword']
        new_password = data['newPassword']
        
        if not current_password or not new_password:
            return jsonify({'message': 'Current password and new password cannot be empty'}), 400
            
        # Pronađi korisnika
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        # Proveri trenutnu lozinku
        if not bcrypt.check_password_hash(user.password, current_password):
            return jsonify({'message': 'Current password is incorrect'}), 401
            
        # Ažuriraj lozinku
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        
        return jsonify({'message': 'Password updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating password: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(debug=True)
