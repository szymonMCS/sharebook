import { useState, useMemo, useCallback, memo, useEffect } from 'react';
import { Inbox, Send } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useUserBooksStore } from '@/store/userBooksStore';
import { LoanRequestCard } from './LoanRequestCard';
import { RequestThread } from '@/components/loan-requests/RequestThread';
import type { LoanRequest } from '@/types';

export function LoanRequestsSection() {
  const { 
    incomingRequests, 
    outgoingRequests, 
    acceptRequest, 
    rejectRequest, 
    cancelRequest,
    fetchRequests,
    isLoading,
    error,
    user
  } = useUserBooksStore();
  
  const [activeTab, setActiveTab] = useState('incoming');
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [selectedRequest, setSelectedRequest] = useState<LoanRequest | null>(null);
  const [isThreadOpen, setIsThreadOpen] = useState(false);

  const pendingIncoming = useMemo(() => {
    return incomingRequests.filter(r => r.status === 'pending');
  }, [incomingRequests]);

  const pendingOutgoing = useMemo(() => {
    return outgoingRequests.filter(r => r.status === 'pending');
  }, [outgoingRequests]);

  const handleCancel = useCallback(async (requestId: string) => {
    setProcessingId(requestId);
    try {
      await cancelRequest(requestId);
    } finally {
      setProcessingId(null);
    }
  }, [cancelRequest]);

  const handleOpenThread = useCallback((request: LoanRequest) => {
    setSelectedRequest(request);
    setIsThreadOpen(true);
  }, []);

  const handleCloseThread = useCallback(() => {
    setIsThreadOpen(false);
    setSelectedRequest(null);
  }, []);

  const handleAccept = useCallback(async () => {
    if (!selectedRequest) return;
    setProcessingId(selectedRequest.id);
    try {
      await acceptRequest(selectedRequest.id);
      handleCloseThread();
    } finally {
      setProcessingId(null);
    }
  }, [selectedRequest, acceptRequest, handleCloseThread]);

  const handleReject = useCallback(async () => {
    if (!selectedRequest) return;
    setProcessingId(selectedRequest.id);
    try {
      await rejectRequest(selectedRequest.id);
      handleCloseThread();
    } finally {
      setProcessingId(null);
    }
  }, [selectedRequest, rejectRequest, handleCloseThread]);

  // Fetch requests on mount
  useEffect(() => {
    fetchRequests();
  }, [fetchRequests]);

  // Sort by date (newest first), pending first
  const sortedIncomingRequests = useMemo(() => {
    return [...incomingRequests].sort((a, b) => {
      if (a.status === 'pending' && b.status !== 'pending') return -1;
      if (a.status !== 'pending' && b.status === 'pending') return 1;
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });
  }, [incomingRequests]);

  const sortedOutgoingRequests = useMemo(() => {
    return [...outgoingRequests].sort((a, b) => {
      if (a.status === 'pending' && b.status !== 'pending') return -1;
      if (a.status !== 'pending' && b.status === 'pending') return 1;
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });
  }, [outgoingRequests]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-serif font-bold text-book-brown">Prośby o wypożyczenie</h1>
        <p className="text-book-muted mt-1">
          Zarządzaj przychodzącymi i wysłanymi prośbami
        </p>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">
          {error}
        </div>
      )}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="incoming" className="relative">
            <Inbox className="w-4 h-4 mr-2" />
            Przychodzące
            {pendingIncoming.length > 0 && (
              <Badge 
                variant="default" 
                className="ml-2 bg-book-gold text-white text-xs px-1.5 py-0"
              >
                {pendingIncoming.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="outgoing" className="relative">
            <Send className="w-4 h-4 mr-2" />
            Wysłane
            {pendingOutgoing.length > 0 && (
              <Badge 
                variant="default" 
                className="ml-2 bg-amber-500 text-white text-xs px-1.5 py-0"
              >
                {pendingOutgoing.length}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Incoming Requests */}
        <TabsContent value="incoming" className="space-y-4">
          {incomingRequests.length === 0 ? (
            <EmptyState 
              icon={<Inbox className="w-12 h-12" />}
              title="Brak przychodzących próśb"
              description="Gdy ktoś poprosi o wypożyczenie Twojej książki, pojawi się tutaj."
            />
          ) : (
            <div className="space-y-3">
              {sortedIncomingRequests.map((request) => (
                <LoanRequestCard
                  key={request.id}
                  request={request}
                  type="incoming"
                  onClick={() => handleOpenThread(request)}
                  isLoading={processingId === request.id || isLoading}
                />
              ))}
            </div>
          )}
        </TabsContent>

        {/* Outgoing Requests */}
        <TabsContent value="outgoing" className="space-y-4">
          {outgoingRequests.length === 0 ? (
            <EmptyState 
              icon={<Send className="w-12 h-12" />}
              title="Brak wysłanych próśb"
              description="Gdy wyślesz prośbę o wypożyczenie książki, pojawi się tutaj."
            />
          ) : (
            <div className="space-y-3">
              {sortedOutgoingRequests.map((request) => (
                <LoanRequestCard
                  key={request.id}
                  request={request}
                  type="outgoing"
                  onCancel={() => handleCancel(request.id)}
                  onClick={() => handleOpenThread(request)}
                  isLoading={processingId === request.id || isLoading}
                />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Request Thread Modal */}
      <RequestThread
        request={selectedRequest}
        isOpen={isThreadOpen}
        onClose={handleCloseThread}
        currentUserId={user?.id || ''}
        type={activeTab as 'incoming' | 'outgoing'}
        onAccept={handleAccept}
        onReject={handleReject}
        isProcessing={!!processingId}
      />
    </div>
  );
}

interface EmptyStateProps { 
  icon: React.ReactNode;
  title: string;
  description: string;
}

const EmptyState = memo(function EmptyState({ 
  icon, 
  title, 
  description 
}: EmptyStateProps) {
  return (
    <div className="bg-white rounded-xl p-12 border border-stone-200/60 text-center">
      <div className="text-stone-300 mx-auto mb-4">{icon}</div>
      <h3 className="font-serif font-semibold text-book-brown mb-2">{title}</h3>
      <p className="text-book-muted text-sm max-w-sm mx-auto">{description}</p>
    </div>
  );
});
