"""Initial database schema with 12 core tables

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-29 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False, unique=True),
        sa.Column('email', sa.String(length=100), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('role', sa.String(length=30), nullable=False, server_default='operator'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])

    # 2. labs
    op.create_table(
        'labs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True),
        sa.Column('code', sa.String(length=30), nullable=False, unique=True),
        sa.Column('building', sa.String(length=100), nullable=False),
        sa.Column('room_number', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_labs_id', 'labs', ['id'])
    op.create_index('ix_labs_name', 'labs', ['name'])
    op.create_index('ix_labs_code', 'labs', ['code'])

    # 3. devices
    op.create_table(
        'devices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lab_id', sa.Integer(), sa.ForeignKey('labs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('device_type', sa.String(length=50), nullable=False),
        sa.Column('mac_address', sa.String(length=50), nullable=False, unique=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='offline'),
        sa.Column('firmware_version', sa.String(length=30), nullable=False, server_default='1.0.0'),
        sa.Column('api_key', sa.String(length=64), nullable=False, unique=True),
        sa.Column('last_heartbeat', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_devices_id', 'devices', ['id'])
    op.create_index('ix_devices_lab_id', 'devices', ['lab_id'])
    op.create_index('ix_devices_mac_address', 'devices', ['mac_address'])
    op.create_index('ix_devices_api_key', 'devices', ['api_key'])

    # 4. device_configs
    op.create_table(
        'device_configs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('sampling_rate_sec', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('reporting_interval_sec', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('sensitivity', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('sleep_mode_enabled', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('config_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_device_configs_id', 'device_configs', ['id'])

    # 5. telemetry_records
    op.create_table(
        'telemetry_records',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id', ondelete='CASCADE'), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('gas_ppm', sa.Float(), nullable=True),
        sa.Column('smoke_detected', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('flame_detected', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('motion_detected', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('power_watts', sa.Float(), nullable=True),
        sa.Column('sound_db', sa.Float(), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_telemetry_records_id', 'telemetry_records', ['id'])
    op.create_index('ix_telemetry_records_device_id', 'telemetry_records', ['device_id'])
    op.create_index('ix_telemetry_records_recorded_at', 'telemetry_records', ['recorded_at'])

    # 6. events
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lab_id', sa.Integer(), sa.ForeignKey('labs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id', ondelete='SET NULL'), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='info'),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_events_id', 'events', ['id'])
    op.create_index('ix_events_lab_id', 'events', ['lab_id'])
    op.create_index('ix_events_event_type', 'events', ['event_type'])
    op.create_index('ix_events_created_at', 'events', ['created_at'])

    # 7. alerts
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lab_id', sa.Integer(), sa.ForeignKey('labs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_id', sa.Integer(), sa.ForeignKey('events.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='active'),
        sa.Column('acknowledged_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('resolved_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_alerts_id', 'alerts', ['id'])
    op.create_index('ix_alerts_lab_id', 'alerts', ['lab_id'])
    op.create_index('ix_alerts_created_at', 'alerts', ['created_at'])

    # 8. policies
    op.create_table(
        'policies',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lab_id', sa.Integer(), sa.ForeignKey('labs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('condition_operator', sa.String(length=10), nullable=False, server_default='>'),
        sa.Column('threshold_value', sa.Float(), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False, server_default='raise_alert'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_policies_id', 'policies', ['id'])
    op.create_index('ix_policies_lab_id', 'policies', ['lab_id'])

    # 9. device_commands
    op.create_table(
        'device_commands',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id', ondelete='CASCADE'), nullable=False),
        sa.Column('issued_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('command_type', sa.String(length=50), nullable=False),
        sa.Column('payload_json', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='pending'),
        sa.Column('response_json', sa.JSON(), nullable=True),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_device_commands_id', 'device_commands', ['id'])
    op.create_index('ix_device_commands_device_id', 'device_commands', ['device_id'])
    op.create_index('ix_device_commands_created_at', 'device_commands', ['created_at'])

    # 10. audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_id', sa.String(length=50), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('details_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])

    # 11. ai_inferences
    op.create_table(
        'ai_inferences',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id', ondelete='SET NULL'), nullable=True),
        sa.Column('lab_id', sa.Integer(), sa.ForeignKey('labs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=30), nullable=False),
        sa.Column('inference_type', sa.String(length=50), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('is_anomaly', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('prediction_output_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_ai_inferences_id', 'ai_inferences', ['id'])
    op.create_index('ix_ai_inferences_lab_id', 'ai_inferences', ['lab_id'])
    op.create_index('ix_ai_inferences_is_anomaly', 'ai_inferences', ['is_anomaly'])
    op.create_index('ix_ai_inferences_created_at', 'ai_inferences', ['created_at'])

    # 12. access_logs
    op.create_table(
        'access_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lab_id', sa.Integer(), sa.ForeignKey('labs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id', ondelete='SET NULL'), nullable=True),
        sa.Column('access_method', sa.String(length=50), nullable=False, server_default='rfid'),
        sa.Column('access_status', sa.String(length=30), nullable=False, server_default='granted'),
        sa.Column('card_uid', sa.String(length=50), nullable=True),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('accessed_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_access_logs_id', 'access_logs', ['id'])
    op.create_index('ix_access_logs_lab_id', 'access_logs', ['lab_id'])
    op.create_index('ix_access_logs_accessed_at', 'access_logs', ['accessed_at'])


def downgrade() -> None:
    op.drop_table('access_logs')
    op.drop_table('ai_inferences')
    op.drop_table('audit_logs')
    op.drop_table('device_commands')
    op.drop_table('policies')
    op.drop_table('alerts')
    op.drop_table('events')
    op.drop_table('telemetry_records')
    op.drop_table('device_configs')
    op.drop_table('devices')
    op.drop_table('labs')
    op.drop_table('users')

