import { useState } from "react";
import { View, Text, TextInput, StyleSheet, TouchableOpacity, ScrollView } from "react-native";
import DropDownPicker from "react-native-dropdown-picker";
import { router } from "expo-router";

export default function ProfileScreen() {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    contactNumber: "",
    address: "",
    gender: "",
    city: "",
    bloodGroup: "",
    role:"",
  });

  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const [genderOpen, setGenderOpen] = useState(false);
  const [genderItems, setGenderItems] = useState([
    { label: "Male", value: "male" },
    { label: "Female", value: "female" },
    { label: "Other", value: "other" },
  ]);

  const [bloodOpen, setBloodOpen] = useState(false);
  const [bloodItems, setBloodItems] = useState([
    { label: "A+", value: "A+" },
    { label: "A-", value: "A-" },
    { label: "B+", value: "B+" },
    { label: "B-", value: "B-" },
    { label: "O+", value: "O+" },
    { label: "O-", value: "O-" },
    { label: "AB+", value: "AB+" },
    { label: "AB-", value: "AB-" },
  ]);

  const [cityOpen, setCityOpen] = useState(false);
  const [cityItems, setCityItems] = useState([
    { label: "Sheikhupura", value: "Sheikhupura" },
    { label: "Lahore", value: "Lahore" },
    { label: "Islamabad", value: "Islamabad" },
    { label: "Faisalabad", value: "Faisalabad" },
  ]);

  // Role dropdown
  const [roleOpen, setRoleOpen] = useState(false);
  const [roleItems, setRoleItems] = useState([
    { label: "Donor", value: "donor" },
    { label: "Needer", value: "needer" },
  ]);

  const validateField = (field, value) => {
    let error = "";
    switch (field) {
      case "firstName":
        if (!value.trim()) error = "First name is required";
        break;
      case "lastName":
        if (!value.trim()) error = "Last name is required";
        break;
      case "gender":
        if (!value) error = "Gender is required";
        break;
      case "contactNumber":
        if (!value.trim()) error = "Contact number is required";
        else if (!/^\d+$/.test(value)) error = "Contact number must be numeric";
        else if (value.length < 11) error = "Must be at least 11 digits";
        break;
      case "city":
        if (!value) error = "City is required";
        break;
      case "address":
        if (!value.trim()) error = "Address is required";
        break;
      case "bloodGroup":
        if (!value) error = "Blood group is required";
        break;
      case "role": // <-- NEW VALIDATION
        if (!value) error = "Please select if you are a Donor or Needer";
        break;
    }
    setErrors((prev) => ({ ...prev, [field]: error }));
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    validateField(field, value);
  };

  const handleBlur = (field) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
    validateField(field, formData[field]);
  };

  const handleDone = () => {
    let isValid = true;
    Object.keys(formData).forEach((field) => {
      validateField(field, formData[field]);
      setTouched((prev) => ({ ...prev, [field]: true }));
      if (formData[field] === "" || errors[field]) isValid = false;
    });

    if (isValid) {
      router.push("/home");
    }
  };

  const getInputStyle = (field) => {
    return touched[field] && errors[field] ? [styles.input, styles.inputError] : styles.input;
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Create your Profile</Text>

      <Text style={styles.label}>First Name</Text>
      <TextInput
        style={getInputStyle("firstName")}
        placeholder="Enter your first name"
        placeholderTextColor="#888"
        value={formData.firstName}
        onChangeText={(text) => handleChange("firstName", text)}
        onBlur={() => handleBlur("firstName")}
      />
      {touched.firstName && errors.firstName && <Text style={styles.errorText}>{errors.firstName}</Text>}

      <Text style={styles.label}>Last Name</Text>
      <TextInput
        style={getInputStyle("lastName")}
        placeholder="Enter your last name"
        placeholderTextColor="#888"
        value={formData.lastName}
        onChangeText={(text) => handleChange("lastName", text)}
        onBlur={() => handleBlur("lastName")}
      />
      {touched.lastName && errors.lastName && <Text style={styles.errorText}>{errors.lastName}</Text>}

      <Text style={styles.label}>Gender</Text>
      <DropDownPicker
        open={genderOpen}
        value={formData.gender}
        items={genderItems}
        setOpen={setGenderOpen}
        setValue={(callback) => {
          const value = callback(formData.gender);
          handleChange("gender", value);
        }}
        setItems={setGenderItems}
        placeholder="Select Gender"
        style={styles.dropdown}
        dropDownContainerStyle={styles.dropdownContainer}
      />
      {touched.gender && errors.gender && <Text style={styles.errorText}>{errors.gender}</Text>}

      <Text style={styles.label}>Contact Number</Text>
      <TextInput
        style={getInputStyle("contactNumber")}
        placeholder="Enter contact number"
        keyboardType="numeric"
        placeholderTextColor="#888"
        value={formData.contactNumber}
        onChangeText={(text) => handleChange("contactNumber", text)}
        onBlur={() => handleBlur("contactNumber")}
      />
      {touched.contactNumber && errors.contactNumber && <Text style={styles.errorText}>{errors.contactNumber}</Text>}

      <Text style={styles.label}>City</Text>
      <DropDownPicker
        open={cityOpen}
        value={formData.city}
        items={cityItems}
        setOpen={setCityOpen}
        setValue={(callback) => {
          const value = callback(formData.city);
          handleChange("city", value);
        }}
        setItems={setCityItems}
        placeholder="Select City"
        style={styles.dropdown}
        dropDownContainerStyle={styles.dropdownContainer}
      />
      {touched.city && errors.city && <Text style={styles.errorText}>{errors.city}</Text>}

      <Text style={styles.label}>Address</Text>
      <TextInput
        style={getInputStyle("address")}
        placeholder="Enter your full address"
        placeholderTextColor="#888"
        value={formData.address}
        onChangeText={(text) => handleChange("address", text)}
        onBlur={() => handleBlur("address")}
      />
      {touched.address && errors.address && <Text style={styles.errorText}>{errors.address}</Text>}

      <Text style={styles.label}>Blood Group</Text>
      <DropDownPicker
        open={bloodOpen}
        value={formData.bloodGroup}
        items={bloodItems}
        setOpen={setBloodOpen}
        setValue={(callback) => {
          const value = callback(formData.bloodGroup);
          handleChange("bloodGroup", value);
        }}
        setItems={setBloodItems}
        placeholder="Select Blood Group"
        style={styles.dropdown}
        dropDownContainerStyle={styles.dropdownContainer}
      />
      {touched.bloodGroup && errors.bloodGroup && <Text style={styles.errorText}>{errors.bloodGroup}</Text>}

       {/* Donor/Needer */}
      <Text style={styles.label}>Role</Text>
      <DropDownPicker
        open={roleOpen}
        value={formData.role}
        items={roleItems}
        setOpen={setRoleOpen}
        setValue={(callback) => {
          const value = callback(formData.role);
          handleChange("role", value);
        }}
        setItems={setRoleItems}
        placeholder="Select Role"
        style={styles.dropdown}
        dropDownContainerStyle={styles.dropdownContainer}
      />
      {touched.role && errors.role && <Text style={styles.errorText}>{errors.role}</Text>}


      <TouchableOpacity style={styles.button} onPress={handleDone}>
        <Text style={styles.buttonText}>Done</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 25,
    justifyContent: "center",
    backgroundColor: "#fff",
    flexGrow: 1,
  },
  title: {
    fontSize: 28,
    textAlign: "center",
    color: "#C40000",
    fontWeight: "bold",
    marginBottom: 20,
  },
  label: {
    fontWeight: "bold",
    marginTop: 10,
    marginBottom: 5,
    color: "#333",
  },
  input: {
    width: "100%",
    borderRadius: 8,
    paddingHorizontal: 15,
    paddingVertical: 10,
    fontSize: 12,
    marginBottom: 5,
    backgroundColor: "#f2f2f2",
    borderWidth: 1,
    borderColor: "#f2f2f2",
  },
  inputError: {
    borderColor: "#ff0000",
  },
  errorText: {
    color: "#ff0000",
    fontSize: 12,
    marginBottom: 5,
  },
  dropdown: {
    backgroundColor: "#f2f2f2",
    marginBottom: 5,
    borderWidth: 1,
    borderColor: "#f2f2f2",
  },
  dropdownContainer: {
    backgroundColor: "#ffffffff",
  },
  button: {
    backgroundColor: "#d40000",
    paddingVertical: 12,
    borderRadius: 25,
    marginTop: 20,
    marginBottom: 10,
    alignItems: "center",
  },
  buttonText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 16,
  },
});
