import { useState } from 'react';
import { View, Text, TextInput, StyleSheet, TouchableOpacity, ScrollView, Platform } from 'react-native';
import DropDownPicker from 'react-native-dropdown-picker';
import { router } from 'expo-router';


export default function ProfileScreen() {
  const [genderOpen, setGenderOpen] = useState(false);
  const [gender, setGender] = useState('');
  const [genderItems, setGenderItems] = useState([
    { label: 'Male', value: 'male' },
    { label: 'Female', value: 'female' },
    { label: 'Other', value: 'other' },
  ]);

  const [bloodOpen, setBloodOpen] = useState(false);
  const [bloodGroup, setBloodGroup] = useState('');
  const [bloodItems, setBloodItems] = useState([
    { label: 'A+', value: 'A+' },
    { label: 'A-', value: 'A-' },
    { label: 'B+', value: 'B+' },
    { label: 'B-', value: 'B-' },
    { label: 'O+', value: 'O+' },
    { label: 'O-', value: 'O-' },
    { label: 'AB+', value: 'AB+' },
    { label: 'AB-', value: 'AB-' },
  ]);
    const handleDone = () => {
    // You can validate and submit data here before navigating
    router.push('/home');
  };


  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View>
        <Text style={styles.title}>Create your Profile</Text>

        <Text style={styles.label}>First Name</Text>
        <TextInput style={styles.input} placeholder="Enter your first name" placeholderTextColor="#888" />

        <Text style={styles.label}>Last Name</Text>
        <TextInput style={styles.input} placeholder="Enter your last name" placeholderTextColor="#888" />
         <Text style={styles.label}>Gender</Text>
        <DropDownPicker
          open={genderOpen}
          value={gender}
          items={genderItems}
          setOpen={setGenderOpen}
          setValue={setGender}
          setItems={setGenderItems}
          placeholder="Select Gender"
          style={styles.dropdown}
          dropDownContainerStyle={styles.dropdownContainer}
          zIndex={3000}
          zIndexInverse={1000}
        />

        <Text style={styles.label}>Contact Number</Text>
        <TextInput style={styles.input} placeholder="Enter contact number" keyboardType="numeric" placeholderTextColor="#888" />

        <Text style={styles.label}>City</Text>
        <TextInput style={styles.input} placeholder="Enter your city" placeholderTextColor="#888" />

        <Text style={styles.label}>Address</Text>
        <TextInput style={styles.input} placeholder="Enter your full address" placeholderTextColor="#888" />

        <Text style={styles.label}>Blood Group</Text>
        <DropDownPicker
          open={bloodOpen}
          value={bloodGroup}
          items={bloodItems}
          setOpen={setBloodOpen}
          setValue={setBloodGroup}
          setItems={setBloodItems}
          placeholder="Select Blood Group"
          style={styles.dropdown}
          dropDownContainerStyle={styles.dropdownContainer}
          zIndex={2000}
          zIndexInverse={2000}
        />

        <TouchableOpacity style={styles.button} onPress={handleDone}>
          <Text style={styles.buttonText}>Done</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 25,
    justifyContent: 'center',
    backgroundColor: '#fff',
    flexGrow: 1,
  },
  title: {
    fontSize: 28,
    textAlign: 'center',
    color: '#C40000',
    fontWeight: 'bold',
    marginBottom: 20,
  },
  label: {
    fontWeight: 'bold',
    marginTop: 10,
    marginBottom: 5,
    color: '#333',
  },
  input: {
    width: '100%',
    borderRadius: 8,
    paddingHorizontal: 15,
    paddingVertical: 10,
    fontSize: 12,
    marginBottom: 5,
    backgroundColor: '#f2f2f2',
  },
  pickerWrapper: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 10,
    paddingHorizontal: Platform.OS === 'ios' ? 0 : 10, // Android requires horizontal padding
    backgroundColor: '#f4f4f4',
    marginBottom: 10,
    height: 45,
    justifyContent: 'center',
  },
  picker: {
    height: 45,
    color: '#000',
  },
  button: {
    backgroundColor: '#d40000',
    paddingVertical: 12,
    borderRadius: 25,
    marginTop: 20,
    marginBottom: 10,
    alignItems: 'center',
    shadowColor: '#d40000',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 3 },
    shadowRadius: 6,
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
});
