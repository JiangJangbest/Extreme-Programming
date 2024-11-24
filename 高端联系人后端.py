from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    bookmarked = db.Column(db.Boolean, default=False)

    def serialize(self):
        # 创建一个字典，包含你想要序列化为 JSON 的字段
        contact_info = {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'bookmarked': self.bookmarked,
        }
        return contact_info


with app.app_context():
    db.create_all()


@app.route('/contacts', methods=['GET'])
def get_contacts():
    contacts = Contact.query.all()
    return jsonify([c.serialize() for c in contacts])


@app.route('/contacts', methods=['POST'])
def add_contact():
    data = request.json
    new_contact = Contact(**data)
    db.session.add(new_contact)
    db.session.commit()
    return jsonify({'message': 'Contact added successfully'})


@app.route('/contacts/search', methods=['GET'])
def search_contacts():
    name = request.args.get('name')
    if name is not None and name != '':
        contacts = Contact.query.filter(Contact.name.ilike(f'%{name}%')).all()
    else:
        contacts = Contact.query.all()

    return jsonify([c.serialize() for c in contacts])


@app.route('/contacts/search/collect', methods=['GET'])
def search_contacts_collect():
    bookmarked = request.args.get('bookmarked')
    if bookmarked is not None and bookmarked != "0":
        contacts = Contact.query.filter(Contact.bookmarked == True).all()
    else:
        contacts = Contact.query.all()

    return jsonify([c.serialize() for c in contacts])


@app.route('/contacts/collect', methods=['GET'])
def collect():
    id = request.args.get('id')
    contact = Contact.query.get(id)
    if contact:
        # 更新 bookmarked 属性
        contact.bookmarked = True
        # 提交数据库会话
        db.session.commit()
        return jsonify({'message': 'Contact bookmarked status updated successfully.'}), 200
    else:
        return jsonify({'message': 'Contact not found.'}), 404


@app.route('/contacts/<int:id>', methods=['PUT'])
def modify_contact(id):
    data = request.json
    contact = Contact.query.get(id)
    if contact:
        for key, value in data.items():
            setattr(contact, key, value)
        db.session.commit()
        return jsonify({'message': 'Contact updated successfully'})
    return jsonify({'message': 'Contact not found'}), 404


@app.route('/contacts/<int:id>', methods=['DELETE'])
def delete_contact(id):
    contact = Contact.query.get(id)
    if contact:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'message': 'Contact deleted successfully'})
    return jsonify({'message': 'Contact not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
