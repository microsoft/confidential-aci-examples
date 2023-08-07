# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import attestation_sidecar_pb2 as attestation__sidecar__pb2


class AttestationContainerStub(object):
    """attestation_container service definition.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.FetchAttestation = channel.unary_unary(
                '/attestation_container.AttestationContainer/FetchAttestation',
                request_serializer=attestation__sidecar__pb2.FetchAttestationRequest.SerializeToString,
                response_deserializer=attestation__sidecar__pb2.FetchAttestationReply.FromString,
                )


class AttestationContainerServicer(object):
    """attestation_container service definition.
    """

    def FetchAttestation(self, request, context):
        """Fetches and returns attestation report, platform certificates, and UVM endorsements (UVM reference info).
        In future it returns Certificate Revocation List (CRL) as well.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AttestationContainerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FetchAttestation': grpc.unary_unary_rpc_method_handler(
                    servicer.FetchAttestation,
                    request_deserializer=attestation__sidecar__pb2.FetchAttestationRequest.FromString,
                    response_serializer=attestation__sidecar__pb2.FetchAttestationReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'attestation_container.AttestationContainer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class AttestationContainer(object):
    """attestation_container service definition.
    """

    @staticmethod
    def FetchAttestation(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/attestation_container.AttestationContainer/FetchAttestation',
            attestation__sidecar__pb2.FetchAttestationRequest.SerializeToString,
            attestation__sidecar__pb2.FetchAttestationReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)