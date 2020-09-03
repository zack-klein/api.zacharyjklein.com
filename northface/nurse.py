import datetime

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app import db


class HealthCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site = db.Column(db.String(120), nullable=False)
    healthy = db.Column(db.Boolean, nullable=False)
    checked_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"HealthCheck({self.id}, {self.todo})"


class HealthCheckSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = HealthCheck
        include_relationships = True
        load_instance = True


def get():
    health_checks = db.session.query(HealthCheck).all()
    health_checks_schema = HealthCheckSchema()
    return [health_checks_schema.dump(hc) for hc in health_checks]


def add(site, healthy):
    """
    Add a health check.
    """
    health_check = HealthCheck(
        site=site, healthy=healthy, checked_at=datetime.datetime.now()
    )
    db.session.add(health_check)
    db.session.commit()
    return {"id": health_check.id}


def delete(id):
    """
    Delete a To Do from the table.
    """
    health_check = (
        db.session.query(HealthCheck).filter(HealthCheck.id == id).first()
    )
    db.session.delete(health_check)
    db.session.commit()
    return {"success": True}
