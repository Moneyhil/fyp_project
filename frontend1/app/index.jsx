import { View, Text, Image, StyleSheet, TouchableOpacity} from 'react-native';
import { useRouter } from 'expo-router'; 

export default function BloodDonationApp() {
  const router = useRouter();
  return (
    <View style={styles.container}>
    <View style={styles.qoutecard}>
      <Text style= {styles.qoutetext}>"Every drop of blood you donate is a silent promise of Hope,a powerful act of love and a lifeline for some one in need."</Text>
      </View>
        <Text style={styles.appname}>"Welcome to the Blood Donation App"</Text>
        <Image
          source={require('../assets/images/mandw.png')} 
          style={styles.image} />
        <View style={styles.card}>
          <Text style={styles.textcard}>"Becuase someone, Somewhere, is counting on you."</Text>
         
         <TouchableOpacity
          style={styles.button}
          onPress={() => router.push('/up&inscreen')}>
          <Text style={styles.buttonLabel}>Donate Now</Text>
        </TouchableOpacity>
        </View>
  
    </View>
  );
}

const styles = StyleSheet.create({
  qoutecard:{
    backgroundColor: '#f7d0d0ff',
    padding: 20,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#e46565ff',
    marginBottom: 20,
    shadowColor: '#f33434ff',
    shadowOpacity: 5,
    shadowRadius: 6,
    width: '90%',
  },
  qoutetext:{
    fontSize: 16,
    fontStyle: 'italic',
    color: '#333',
    textAlign: 'center',
  },
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  appname: {
    marginLeft:60,
    fontSize: 24,
    fontWeight: 'bold',
  },
  image: {
    marginTop:0,
    width: 300,
    height: 300,
    resizeMode: 'contain',
  },
  card:{
    backgroundColor: '#f7d0d0ff',
    padding: 20,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#e46565ff',
    marginBottom: 20,
    shadowColor: '#f33434ff',
    shadowOpacity: 5,
    shadowRadius: 6,
    width: '90%',
  },
  textcard:{
    fontSize: 16,
    fontWeight: '600',
    fontStyle: 'italic',
    color: '#333',
    textAlign: 'center',
  },
  button:{
    backgroundColor: '#64cbfaff',  
    paddingVertical: 12,
    paddingHorizontal: 25,
    borderRadius: 25,
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 10,
    shadowColor: '#4a58a5ff',
    shadowOpacity: 5,
    shadowRadius: 6,
  },
  buttonLabel:{
    color: '#0e0b0aff',
    fontWeight:'700'
  },

})

