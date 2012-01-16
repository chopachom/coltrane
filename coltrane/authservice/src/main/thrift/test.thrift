# time.thrift
namespace java io.coltrane.auth.thrift
typedef i64 Timestamp
service TimeServer {
   Timestamp time()
}
