import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.device import Device, DeviceModel
from app.models.device_config import DeviceConfig
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceRegisterRequest
from app.core.errors import NotFoundError, ConflictError


class DeviceService:
    @staticmethod
    def register_agent_device(db: Session, data: DeviceRegisterRequest) -> DeviceModel:
        """
        Register or heartbeat-update a monitored PC/agent in Supabase DB.
        """
        device = db.query(DeviceModel).filter(DeviceModel.device_id == data.device_id).first()
        if device:
            if data.hostname:
                device.hostname = data.hostname
            if data.ip:
                device.ip = data.ip
            if data.os:
                device.os = data.os
            if data.agent_version:
                device.agent_version = data.agent_version
            device.status = "online"
        else:
            device = DeviceModel(
                id=str(uuid.uuid4()),
                device_id=data.device_id,
                hostname=data.hostname,
                ip=data.ip,
                os=data.os,
                agent_version=data.agent_version or "1.0.0",
                status="online",
            )
            db.add(device)

        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def get_devices(db: Session, skip: int = 0, limit: int = 100, lab_id: Optional[int] = None) -> List[Device]:
        query = db.query(Device)
        if lab_id:
            query = query.filter(Device.lab_id == lab_id)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_device_by_id(db: Session, device_id: int) -> Device:
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise NotFoundError("Device", device_id)
        return device

    @staticmethod
    def get_device_by_mac(db: Session, mac_address: str) -> Optional[Device]:
        return db.query(Device).filter(Device.mac_address == mac_address).first()

    @staticmethod
    def create_device(db: Session, data: DeviceCreate) -> Device:
        existing = db.query(Device).filter(Device.mac_address == data.mac_address).first()
        if existing:
            raise ConflictError(f"Device with MAC address '{data.mac_address}' already exists")

        device = Device(
            name=data.name,
            device_type=data.device_type,
            mac_address=data.mac_address,
            lab_id=data.lab_id,
            ip_address=data.ip_address,
            firmware_version=data.firmware_version,
            status="offline",
        )
        db.add(device)
        db.flush()

        # Add initial config
        cfg_data = data.config
        config = DeviceConfig(
            device_id=device.id,
            sampling_rate_sec=cfg_data.sampling_rate_sec if cfg_data else 5,
            reporting_interval_sec=cfg_data.reporting_interval_sec if cfg_data else 30,
            sensitivity=cfg_data.sensitivity if cfg_data else "medium",
            sleep_mode_enabled=cfg_data.sleep_mode_enabled if cfg_data else False,
            config_json=cfg_data.config_json if cfg_data else {},
        )
        db.add(config)
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def update_device(db: Session, device_id: int, data: DeviceUpdate) -> Device:
        device = DeviceService.get_device_by_id(db, device_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(device, key, value)
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def delete_device(db: Session, device_id: int) -> bool:
        device = DeviceService.get_device_by_id(db, device_id)
        db.delete(device)
        db.commit()
        return True

    @staticmethod
    def record_heartbeat(db: Session, device_id: int, ip_address: Optional[str] = None) -> Device:
        device = DeviceService.get_device_by_id(db, device_id)
        device.last_heartbeat = datetime.now(timezone.utc)
        device.status = "online"
        if ip_address:
            device.ip_address = ip_address
        db.commit()
        db.refresh(device)
        return device


device_service = DeviceService()

