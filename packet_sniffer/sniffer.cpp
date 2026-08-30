#include<iostream>
#include<sys/socket.h>
#include<arpa/inet.h>
#include<netinet/ip.h>
#include<unistd.h>
#include<linux/if_ether.h>
#include<netinet/tcp.h>
#include<netinet/udp.h>
#include<cstring>
#include<fstream>
#include<ctime>
#include<sys/types.h>
#include<netinet/in.h>
#include<cctype>  //used for isprint()
using namespace std;

bool SHOW_TCP=true;
bool SHOW_UDP=true;
bool SHOW_DNS=true;
int is_save_file=0;  //flag for saving the file
int is_gui=0;
int server_fd;        // server socket for establishing communication with python
int client_socket;    //socket for data transfer to python
ofstream pcap_file;
struct pcap_global_header{
  uint32_t magic_number;
  uint16_t version_major;
  uint16_t version_minor;
  uint32_t thiszone;
  uint32_t sigfigs;
  uint32_t snaplen;
  uint32_t network;
};
struct pcap_packet_header{
  uint32_t ts_sec;
  uint32_t ts_usec;
  uint32_t incl_len;
  uint32_t orig_len;
};
struct DNS_HEADER{
  unsigned short id;

  unsigned char rd :1;
  unsigned char tc :1;
  unsigned char aa :1;
  unsigned char opcode :4;
  unsigned char qr :1;

  unsigned char rcode :4;
  unsigned char cd :1;
  unsigned char ad :1;
  unsigned char z :1;
  unsigned char ra :1;

  unsigned short q_count;
  unsigned short ans_count;
  unsigned short auth_count;
  unsigned short add_count;
};
string extract_dns_name(unsigned char *reader){
  string domain="";
  while(*reader!=0){
    int length=*reader;
    reader++;
    for(int i=0;i<length;i++){
      domain+=*reader;
      reader++;
    }
    domain+='.';
  }
  if(!domain.empty()){
    domain.pop_back();
  }
  return domain;
}
void parse_dns_packet(unsigned char *buffer,struct iphdr *ip_header,int data_size){
  unsigned short ip_header_length=ip_header->ihl*4;
  struct udphdr *udp_header=(struct udphdr*)(buffer+sizeof(struct ethhdr)+ip_header_length);
  unsigned char *dns_start=buffer+sizeof(struct ethhdr)+ip_header_length+sizeof(udphdr);
  struct DNS_HEADER *dns=(struct DNS_HEADER*)dns_start;
  unsigned char *query_name=dns_start+sizeof(struct DNS_HEADER);
  string domain=extract_dns_name(query_name);
  cout<<"\n============ DNS QUERY ============\n";
  cout<<"Domain Requested :"<<domain<<endl;
}
void print_payload(unsigned char *data,int size){
  cout<<"\nPayload Data: \n";
  for(int i=0;i<size;i++){
    //Hex dump
    printf("%02X ",data[i]);
    //New line every 16 bytes
    if((i%1)%16==0){
      cout<<endl;
    }
  }
  cout<<"\n\nASCII View:\n";
  for(int i=0;i<size;i++){
    if(isprint(data[i])){
      cout<<(char)data[i];
    }
    else{
      cout<<".";
    }
  }
  cout<<endl;
}
//http detection function
bool is_http_data(unsigned char *data,int size){
  if(size<=0){
    return false;
  }
  string payload((char*)data,size);
  if(payload.find("GET")!=string::npos) return true;
  if(payload.find("POST")!=string::npos) return true;
  if(payload.find("HTTP")!=string::npos) return true;
  return false;
}
int create_raw_socket(){
  int sock_raw=socket(AF_PACKET,SOCK_RAW,htons(ETH_P_ALL));
  if(sock_raw<0){
    perror("Socket Error");
    exit(1);
  }
  return sock_raw;
}
void print_separator(){
  cout<<"\n=======================================================\n";
}
void print_tcp_flags(struct tcphdr *tcp_header){
  cout<<" TCP Flags      : ";
  if(tcp_header->syn) cout<<"SYN ";
  if(tcp_header->ack) cout<<"ACK ";
  if(tcp_header->fin) cout<<"FIN ";
  if(tcp_header->psh) cout<<"PSH ";
  if(tcp_header->rst) cout<<"RST ";
  cout<<endl;
}
void parse_tcp_packet(unsigned char *buffer,struct iphdr *ip_header,int data_size){
  unsigned short ip_header_length=ip_header->ihl*4;
  struct tcphdr *tcp_header=(struct tcphdr*)(buffer+sizeof(struct ethhdr)+ip_header_length);
  unsigned short tcp_header_length=tcp_header->doff*4;
  unsigned char *payload=buffer+sizeof(struct ethhdr)+ip_header_length+tcp_header_length;
  int payload_size=data_size-(sizeof(struct ethhdr)+ip_header_length+tcp_header_length);
  int source_tcp_port=ntohs(tcp_header->source);
  int dest_tcp_port=ntohs(tcp_header->dest);

  cout<<"Source Port       :"<<source_tcp_port<<endl;
  cout<<"Destination Port  :"<<dest_tcp_port<<endl;
  cout<<"Sequence Number   :"<<ntohs(tcp_header->seq)<<endl;
  cout<<"Ack number        :"<<ntohl(tcp_header->ack_seq)<<endl;
  print_tcp_flags(tcp_header);
  if(payload_size>0){
    if(is_http_data(payload,payload_size)){
      cout<<"\n================ HTTP DATA DETECTED =================\n";
    }
    print_payload(payload,payload_size);
  }
}
void parse_udp_packet(unsigned char *buffer,struct iphdr *ip_header,int data_size){
  unsigned short ip_header_length=ip_header->ihl*4;
  struct udphdr *udp_header=(struct udphdr*)(buffer+sizeof(struct ethhdr)+ip_header_length);
  int source_port=ntohs(udp_header->source);
  int destination_port=ntohs(udp_header->dest);
  cout<<"Source port    :"<<source_port<<endl;
  cout<<"Destination Port:"<<destination_port<<endl;

  if(source_port==53 || destination_port==53){
    if(SHOW_DNS){
      parse_dns_packet(buffer,ip_header,data_size);
    }
  }
}
const char* get_protocol_name(int protocol){
  switch(protocol){
    case 1:
      return "ICMP";
    case 2:
      return "IGMP";
    case 6:
      return "TCP";
    case 17:
      return "UDP";
    default:
      return "OTHER";
  }
}
void send_to_gui(string src_ip,string dst_ip,string protocol);
void print_ip_address(struct iphdr *ip_header){
  struct sockaddr_in source,dest;
  memset(&source,0,sizeof(source));
  memset(&dest,0,sizeof(dest));
  source.sin_addr.s_addr=ip_header->saddr;
  dest.sin_addr.s_addr=ip_header->daddr;
  cout<<"Source IP      :"<<inet_ntoa(source.sin_addr)<<endl;
  cout<<"Destination IP :"<<inet_ntoa(dest.sin_addr)<<endl;
  //---python data communication------
  if(is_gui==1){
    string src_ip=inet_ntoa(source.sin_addr);
    string dst_ip=inet_ntoa(dest.sin_addr);
    string protocol=get_protocol_name(ip_header->protocol);
    send_to_gui(src_ip,dst_ip,protocol);
  }
}
void print_protocol(struct iphdr *ip_header){
  cout<<"Protocol       :"<<get_protocol_name(ip_header->protocol)<<endl;
}
void save_packet_to_pcap(unsigned char *buffer,int data_size);
void process_packet(unsigned char *buffer,int data_size){
  if(is_save_file==1) save_packet_to_pcap(buffer,data_size);   /// used to save the pcap file here
  struct iphdr *ip_header=(struct iphdr*)(buffer+sizeof(struct ethhdr));
  //==============ADDING THE PORT 9090 FILTER================
  if(ip_header->protocol==6){
    unsigned short ip_header_length=ip_header->ihl*4;
    struct tcphdr *tcp_header=(struct tcphdr*)(buffer+sizeof(struct ethhdr)+ip_header_length);
    int tcp_source_port=ntohs(tcp_header->source);
    int tcp_dest_port=ntohs(tcp_header->dest);
    if(tcp_source_port==9090 || tcp_dest_port==9090) return;
  }
  //===============================================================
  print_separator();
  print_ip_address(ip_header);
  print_protocol(ip_header);
  cout<<"Packet Size    :"<<data_size<<" bytes"<<endl;
  switch(ip_header->protocol){
    case 6:
      if(SHOW_TCP){
        parse_tcp_packet(buffer,ip_header,data_size);
      }
      break;
    case 17:
      if(SHOW_UDP){
        parse_udp_packet(buffer,ip_header,data_size);
      }
      break;
  }

}
void start_sniffing(int sock_raw){
  unsigned char buffer[65536];
  while(true){
    int data_size=recvfrom(sock_raw,buffer,sizeof(buffer),0,NULL,NULL);
    if(data_size<0){
      perror("Recvfrom Error");
      close(sock_raw);
      exit(1);
    }
    process_packet(buffer,data_size);
  }
}
//-----------------packet saving area---------------------------------------
void initialize_pcap_file(){
  pcap_global_header global_header;

  global_header.magic_number=0xa1b2c3d4;
  global_header.version_major=2;
  global_header.version_minor=4;
  global_header.thiszone=0;
  global_header.sigfigs=0;
  global_header.snaplen=65535;
  global_header.network=1;   //network=1 means ethernet packets 

  pcap_file.open("capture.pcap",ios::binary);
  pcap_file.write((char*)&global_header,sizeof(global_header));
  cout<<"PCAP file initialized. \n";
}
void save_packet_to_pcap(unsigned char *buffer,int data_size){
  pcap_packet_header packet_header;

  packet_header.ts_sec=time(NULL);
  packet_header.ts_usec=0;

  packet_header.incl_len=data_size;
  packet_header.orig_len=data_size;

  pcap_file.write((char*)&packet_header,sizeof(packet_header));
  pcap_file.write((char*)buffer,data_size);
}
//------------------------------------------web dashboard communication----------------------
void initialize_gui_server(){
  struct sockaddr_in address;
  
  int opt=1;
  int addrlen=sizeof(address);

  server_fd=socket(AF_INET,SOCK_STREAM,0);
  if(server_fd==0){
    perror("Socket failed");
    exit(EXIT_FAILURE);
  }
  setsockopt(server_fd,SOL_SOCKET,SO_REUSEADDR,&opt,sizeof(opt));

  address.sin_family=AF_INET;
  address.sin_addr.s_addr=INADDR_ANY;
  address.sin_port=htons(9090);
  if((bind(server_fd,(struct sockaddr*)&address,sizeof(address)))<0){
    perror("bind failed");
    exit(EXIT_FAILURE);
  }
  if((listen(server_fd,3))<0){
    perror("listening failed");
    exit(EXIT_FAILURE);
  }
  cout<<"Waiting for FastAPI dashboard...."<<endl;
  client_socket=accept(server_fd,(struct sockaddr*)&address,(socklen_t*)&addrlen);
  cout<<"Dashboard connected."<<endl;
}
void send_to_gui(string src_ip,string dst_ip,string protocol){
  string json_data=
    "{"
    "\"src_ip\":\""+src_ip+"\","
    "\"dst_ip\":\""+dst_ip+"\","
    "\"protocol\":\""+protocol+"\""
    "}\n";
  send(client_socket,json_data.c_str(),json_data.size(),0);
}
int main(){
  cout<<"Do you want to save the file (Y=1/N=0):";
  cin>>is_save_file;
  cout<<"Do you want web dashboard support (Y=1/N=0):";
  cin>>is_gui;
  if(is_save_file==1) initialize_pcap_file(); //initializing the pcap file
  if(is_gui==1) initialize_gui_server();
  int sock_raw=create_raw_socket();
  cout<<"Sniffer started....\n";
  start_sniffing(sock_raw);
  if(is_save_file==1) pcap_file.close();
  if(is_gui==1){
    close(client_socket);
    close(server_fd);
  }
  close(sock_raw);
  return 0;
}
